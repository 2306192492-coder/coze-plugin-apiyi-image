import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import queue
import requests
import re
import os
import json
import socket
from datetime import datetime
from urllib.parse import urlparse
from urllib3.util import parse_url
import html
import ipaddress
from bs4 import BeautifulSoup

# ================= 自定义异常 =================

class SecurityError(Exception):
    pass

class NetworkError(Exception):
    pass

# ================= 配置管理 =================

class Config:
    DEFAULT_API_URL = "https://api.apiyi.com/v1/chat/completions"
    DEFAULT_MODEL = "gpt-3.5-turbo"
    CONFIG_FILE = "config.json"
    
    _api_key = os.getenv("AI_API_KEY", "")
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive"
    }
    
    REQUEST_TIMEOUT = 15
    AI_TIMEOUT = 30

    @classmethod
    def get_api_key(cls):
        return cls._api_key

    @classmethod
    def set_api_key(cls, value):
        cls._api_key = value

# ================= 安全工具函数 =================

def is_safe_url(url):
    """防止 SSRF：严格检查 URL 协议和 IP 地址"""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            return False
        
        hostname = parsed.hostname
        if not hostname:
            return False
            
        # 检查是否为 IP 地址格式，如果是则直接验证
        try:
            ip_obj = ipaddress.ip_address(hostname)
            return not (ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast)
        except ValueError:
            pass
            
        # 解析域名
        # 注意：生产环境中应使用更复杂的 DNS 解析逻辑防止 DNS Rebinding
        # 这里仅做基础演示，实际应限制 requests 的 redirect 行为
        ip_addresses = socket.getaddrinfo(hostname, None)
        
        for family, _, _, _, addr in ip_addresses:
            ip = addr[0]
            try:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast:
                    return False
            except ValueError:
                continue
        return True
    except Exception:
        return False

# ================= 核心逻辑 =================

class VideoExtractor:
    def __init__(self):
        self.session = None

    def __enter__(self):
        self.session = requests.Session()
        self.session.headers.update(Config.HEADERS)
        # 关键安全修复：禁止自动跟随重定向，防止 SSRF 通过 302 跳转绕过
        self.session.allow_redirects = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()

    def _fetch_html(self, url):
        if not is_safe_url(url):
            raise SecurityError(f"禁止访问该 URL (可能存在安全风险): {url}")
            
        try:
            # 手动处理重定向以确保目标地址安全
            response = self.session.get(url, timeout=Config.REQUEST_TIMEOUT, allow_redirects=False)
            
            if response.is_redirect:
                location = response.headers.get('Location')
                if location and not is_safe_url(location):
                    raise SecurityError(f"重定向目标不安全：{location}")
                # 如果安全，可以手动请求一次，此处简化为报错或允许一次安全重定向
                # 为简化代码，此处若发现重定向且目标安全，则再次请求（生产环境需限制重定向次数）
                if location:
                     response = self.session.get(location, timeout=Config.REQUEST_TIMEOUT, allow_redirects=False)
            
            response.raise_for_status()
            
            if response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding
            return response.text
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"网络请求失败：{str(e)}") from e

    def _decode_html_entities(self, text):
        if not text:
            return ""
        return html.unescape(text)

    def extract_douyin(self, url):
        try:
            html_content = self._fetch_html(url)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 策略 1: Meta Description
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            if desc_tag and desc_tag.get('content'):
                content = self._decode_html_entities(desc_tag['content'])
                if len(content) > 20:
                    return f"【抖音文案】\n{content}"

            # 策略 2: 查找 SIGI_STATE (使用 BeautifulSoup 查找 script 标签)
            script_tags = soup.find_all('script', attrs={'id': 'SIGI_STATE'})
            if script_tags:
                try:
                    json_str = script_tags[0].string
                    if json_str:
                        data = json.loads(json_str)
                        if isinstance(data, dict) and 'video' in data:
                            video_info = data['video']
                            if isinstance(video_info, dict) and 'desc' in video_info:
                                return f"【抖音文案 (JSON 解析)】\n{self._decode_html_entities(str(video_info['desc']))}"
                except (json.JSONDecodeError, KeyError, TypeError, AttributeError):
                    pass

            return "【抖音文案提取提示】\n成功访问页面，但未能提取完整文案。\n原因：抖音采用强动态渲染和反爬。\n建议：生产环境请使用官方 API 或专业解析服务。"
            
        except Exception as e:
            return f"【抖音提取错误】\n{str(e)}"

    def extract_xiaohongshu(self, url):
        try:
            html_content = self._fetch_html(url)
            soup = BeautifulSoup(html_content, 'html.parser')
            content_parts = []
            
            title_tag = soup.find('title')
            if title_tag:
                content_parts.append(f"标题：{self._decode_html_entities(title_tag.get_text(strip=True))}")
                
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            if desc_tag and desc_tag.get('content'):
                clean_desc = self._decode_html_entities(desc_tag['content'])
                content_parts.append(f"内容：{clean_desc}")
                
            if content_parts:
                return "【小红书文案】\n" + "\n".join(content_parts)
                
            return "【小红书文案提取提示】\n未找到标准 Meta 描述，可能需要登录 Cookie。"
        except Exception as e:
            return f"【小红书提取错误】\n{str(e)}"

    def extract_generic(self, url):
        try:
            html_content = self._fetch_html(url)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            if desc_tag and desc_tag.get('content'):
                content = self._decode_html_entities(desc_tag['content'])
                return f"【通用提取】\n{content}"
            
            body = soup.find('body')
            if body:
                # 移除 script 和 style 标签
                for tag in body(['script', 'style']):
                    tag.decompose()
                text = body.get_text(separator=' ', strip=True)
                return f"【通用提取 (片段)】\n{text[:500]}..."
                
            return "未能提取到任何有效文本内容。"
        except Exception as e:
            return f"【通用提取错误】\n{str(e)}"

    def extract(self, url):
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        if "douyin.com" in domain or "tiktok.com" in domain:
            return self.extract_douyin(url)
        elif "xiaohongshu.com" in domain or "xhslink.com" in domain:
            return self.extract_xiaohongshu(url)
        else:
            return self.extract_generic(url)

class AIAnalyzer:
    def __init__(self, api_key, model, url):
        self.api_key = api_key
        self.model = model
        self.url = url
        self.session = None

    def __enter__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()

    def analyze(self, content):
        if not self.api_key:
            return "错误：未提供 API Key，无法进行 AI 分析。"
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个短视频爆款逻辑分析专家。请分析以下文案的亮点、结构、情绪钩子和潜在爆款原因。"},
                {"role": "user", "content": f"视频来源：{self.url}\n\n文案内容：\n{content}"}
            ],
            "temperature": 0.7
        }
        
        try:
            response = self.session.post(Config.DEFAULT_API_URL, json=payload, timeout=Config.AI_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['message']['content']
            return "AI 返回格式异常，未找到分析结果。"
        except requests.exceptions.RequestException as e:
            return f"AI 请求失败：{str(e)}"
        except Exception as e:
            return f"分析过程出错：{str(e)}"

# ================= GUI 界面 =================

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("视频文案提取与 AI 分析工具")
        self.root.geometry("800x600")
        
        self.result_queue = queue.Queue()
        
        self.create_widgets()
        self.check_queue()
        
    def create_widgets(self):
        # 输入区域
        input_frame = ttk.LabelFrame(self.root, text="输入配置", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(input_frame, text="视频链接:").grid(row=0, column=0, sticky="w")
        self.url_entry = ttk.Entry(input_frame, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="API Key:").grid(row=1, column=0, sticky="w")
        self.api_key_entry = ttk.Entry(input_frame, width=50, show="*")
        self.api_key_entry.grid(row=1, column=1, padx=5, pady=5)
        self.api_key_entry.insert(0, Config.get_api_key())
        
        # 按钮区域
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        self.extract_btn = ttk.Button(btn_frame, text="提取文案", command=self.start_extraction)
        self.extract_btn.pack(side="left", padx=5)
        
        self.analyze_btn = ttk.Button(btn_frame, text="AI 分析", command=self.start_analysis)
        self.analyze_btn.pack(side="left", padx=5)
        self.analyze_btn.config(state="disabled")
        
        # 输出区域
        output_frame = ttk.LabelFrame(self.root, text="结果输出", padding=10)
        output_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=20)
        self.output_text.pack(fill="both", expand=True)
        
        self.current_content = ""

    def start_extraction(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("警告", "请输入视频链接")
            return
            
        self.extract_btn.config(state="disabled")
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "正在提取...\n")
        
        thread = threading.Thread(target=self.run_extraction, args=(url,))
        thread.daemon = True
        thread.start()

    def run_extraction(self, url):
        try:
            with VideoExtractor() as extractor:
                result = extractor.extract(url)
                self.result_queue.put(('extraction_done', result))
        except Exception as e:
            self.result_queue.put(('error', str(e)))

    def start_analysis(self):
        if not self.current_content:
            messagebox.showwarning("警告", "请先提取文案")
            return
            
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showwarning("警告", "请输入 API Key")
            return
            
        Config.set_api_key(api_key)
        
        self.analyze_btn.config(state="disabled")
        self.output_text.insert(tk.END, "\n--- 正在 AI 分析 ---\n")
        
        thread = threading.Thread(target=self.run_analysis, args=(api_key,))
        thread.daemon = True
        thread.start()

    def run_analysis(self, api_key):
        try:
            with AIAnalyzer(api_key, Config.DEFAULT_MODEL, self.url_entry.get()) as analyzer:
                result = analyzer.analyze(self.current_content)
                self.result_queue.put(('analysis_done', result))
        except Exception as e:
            self.result_queue.put(('error', str(e)))

    def check_queue(self):
        try:
            while True:
                msg_type, data = self.result_queue.get_nowait()
                
                if msg_type == 'extraction_done':
                    self.current_content = data
                    self.output_text.delete(1.0, tk.END)
                    self.output_text.insert(tk.END, data)
                    self.extract_btn.config(state="normal")
                    self.analyze_btn.config(state="normal")
                    
                elif msg_type == 'analysis_done':
                    self.output_text.insert(tk.END, f"\n\n{data}")
                    self.analyze_btn.config(state="normal")
                    
                elif msg_type == 'error':
                    self.output_text.insert(tk.END, f"\n发生错误：{data}")
                    self.extract_btn.config(state="normal")
                    self.analyze_btn.config(state="normal")
                    messagebox.showerror("错误", data)
                    
        except queue.Empty:
            pass
        
        self.root.after(100, self.check_queue)

if __name__ == "__main__":
    # 确保安装了 beautifulsoup4 和 lxml: pip install beautifulsoup4 lxml
    root = tk.Tk()
    app = App(root)
    root.mainloop()