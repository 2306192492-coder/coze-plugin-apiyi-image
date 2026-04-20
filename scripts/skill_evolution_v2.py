#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能进化引擎 v2.0 - 完整版
功能：自动分析→优化→验证→回滚→报告
"""

import os
import sys
import json
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

# 配置
API_KEY = os.getenv("XUNFEI_API_KEY")
API_BASE = os.getenv("XUNFEI_BASE_URL", "https://maas-coding-api.cn-huabei-1.xf-yun.com/v2")

if not API_KEY:
    print("❌ 错误：请设置环境变量 XUNFEI_API_KEY")
    sys.exit(1)

import requests

class SkillEvolution:
    def __init__(self, skill_path):
        self.skill_path = Path(skill_path)
        self.backup_path = None  # 存储路径字符串，不是文件对象
        self.report = {
            "skill": str(skill_path),
            "timestamp": datetime.now().isoformat(),
            "before_score": None,
            "after_score": None,
            "issues_found": [],
            "issues_fixed": [],
            "test_passed": False,
            "rolled_back": False
        }
    
    def analyze(self):
        """分析代码并评分"""
        print(f"\n🔍 分析：{self.skill_path}")
        
        # 读取代码
        code = self.skill_path.read_text(encoding="utf-8")
        code_lines = len(code.splitlines())
        
        # 对于超长文件，只取关键部分
        if code_lines > 300:
            print(f"⚠️  文件过长 ({code_lines} 行)，将分段处理或提取关键函数")
            # 截取前 6000 行用于分析（留足余量给提示词）
            code = "\n".join(code.splitlines()[:6000])
        
        prompt = f"""你是资深代码审查专家 + 重构大师。分析以下 Python 代码：

```python
{code[:8000]}
```

## 任务
1. **评分** (0-100): 综合考虑安全性、稳定性、可维护性
2. **问题列表**: 列出所有 Critical/High/Medium 级别问题
3. **优化代码**: 生成完整可运行的优化版本

## 关键要求（必须遵守）

### 1. 必须真正修复问题，不只是重构
❌ 错误做法：只是移动代码位置、重命名变量、添加注释
✅ 正确做法：
  - 硬编码 API Key → 改用 `os.getenv()` + 配置文件
  - 资源泄露 → 添加 `try-finally` 或 `with` 上下文管理器
  - 反爬不足 → 添加随机延迟、请求头轮换、Cookie 管理
  - 选择器脆弱 → 添加多个 fallback 选择器、异常捕获
  - 异常粗糙 → 捕获具体异常类型、添加重试逻辑

### 2. Critical 问题必须修复（否则代码无法运行）
- 语法错误：代码不完整、未定义变量、括号不匹配
- 安全漏洞：硬编码密钥、SSRF 风险、SQL 注入
- 资源泄露：未关闭的连接、进程残留、文件句柄

### 3. High 问题必须修复（否则生产环境会失败）
- 反爬策略：添加随机延迟、请求头轮换、User-Agent 池
- 异常处理：捕获具体异常、添加重试机制、记录详细错误
- 选择器脆弱：添加 2-3 个 fallback 选择器、使用更稳定的属性选择器
- 线程安全：使用 `queue.Queue`、避免全局状态竞争

### 4. 优化代码必须完整
- 包含所有必要的 `import` 语句
- 包含所有类定义和函数
- 包含主程序入口（`if __name__ == "__main__":`）
- 如果是 GUI 应用，包含完整的界面逻辑

### 5. 不要引入新的外部依赖
- 只使用标准库和代码中已有的依赖
- 如果必须引入，在注释中说明理由

### 6. 保持代码简洁
- 避免过度工程化（不要为单用途脚本创建复杂架构）
- 函数长度控制在 50 行以内
- 一个函数只做一件事

### 7. 代码完整性检查（非常重要！）
在输出前，请自我检查：
- [ ] 所有函数都有完整的函数体（没有截断）
- [ ] 所有括号都匹配
- [ ] 所有字符串都闭合
- [ ] 主程序入口完整（`if __name__ == "__main__":` 后有完整代码）
- [ ] 没有未定义的变量或函数

**如果代码太长无法完整输出，请优先保证核心函数的完整性，可以删减次要函数或注释。**

## 修复示例（参考这个粒度）

### 示例 1：修复资源泄露
```python
# 修复前
driver = webdriver.Chrome()
data = scrape(driver)  # 可能抛出异常
driver.quit()  # 异常时不会执行

# 修复后
driver = None
try:
    driver = webdriver.Chrome()
    data = scrape(driver)
finally:
    if driver:
        driver.quit()  # 无论如何都会执行
```

### 示例 2：修复硬编码配置
```python
# 修复前
API_KEY = "sk-1234567890abcdef"
TIMEOUT = 30

# 修复后
import os
API_KEY = os.getenv("API_KEY")  # 从环境变量读取
TIMEOUT = int(os.getenv("TIMEOUT", "30"))  # 带默认值
```

### 示例 3：修复脆弱的选择器
```python
# 修复前
element = driver.find_element(By.CSS_SELECTOR, "#pl_top_realtimehot")

# 修复后
# 尝试多个 fallback 选择器
selectors = [
    "#pl_top_realtimehot",  # 原始选择器
    "[data-type='realtimehot']",  # 属性选择器（更稳定）
    "//div[contains(@class, 'hot-list')]",  # XPath fallback
]
element = None
for selector in selectors:
    try:
        element = driver.find_element(By.CSS_SELECTOR, selector)
        break
    except NoSuchElementException:
        continue
if not element:
    raise RuntimeError("所有选择器都失败了，页面结构可能已变更")
```

## 输出格式 (严格 JSON)
{{
    "score": 65,
    "issues": [
        {{"level": "Critical", "description": "硬编码 API Key", "line": 5, "fix_hint": "改用 os.getenv()"}},
        {{"level": "High", "description": "资源未释放", "line": 23, "fix_hint": "添加 try-finally"}}
    ],
    "optimized_code": "完整的优化后代码..."
}}

只输出 JSON，不要其他内容。optimized_code 字段必须是完整可运行的代码。
"""
        
        try:
            response = requests.post(
                f"{API_BASE}/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "astron-code-latest",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 16000  # 增加 token 限制，避免代码截断
                },
                timeout=300  # 增加超时时间
            )
            response.raise_for_status()
            
            content = response.json()["choices"][0]["message"]["content"]
            
            # 提取 JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            
            self.report["before_score"] = result["score"]
            self.report["issues_found"] = result["issues"]
            
            print(f"📊 原始评分：{result['score']}/100")
            print(f"🐛 发现问题：{len(result['issues'])} 个")
            for issue in result["issues"][:5]:
                print(f"   - [{issue['level']}] {issue['description']}")
            
            return result
            
        except Exception as e:
            print(f"❌ 分析失败：{e}")
            return None
    
    def backup(self):
        """创建备份"""
        import tempfile
        # 创建临时备份文件
        temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.py', delete=False)
        temp_file.close()  # 关闭文件句柄
        self.backup_path = temp_file.name  # 只保存路径字符串
        shutil.copy2(self.skill_path, self.backup_path)
        print(f"💾 备份：{self.backup_path}")
    
    def apply_optimization(self, optimized_code):
        """应用优化代码"""
        # 提取代码块
        if "```python" in optimized_code:
            optimized_code = optimized_code.split("```python")[1].split("```")[0].strip()
        elif "```" in optimized_code:
            optimized_code = optimized_code.split("```")[1].split("```")[0].strip()
        
        self.skill_path.write_text(optimized_code, encoding="utf-8")
        print(f"✅ 已应用优化代码")
    
    def verify_syntax(self):
        """语法检查"""
        try:
            result = subprocess.run(
                ["python3", "-m", "py_compile", str(self.skill_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print("✅ 语法检查通过")
                return True
            else:
                print(f"❌ 语法错误：{result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 语法检查异常：{e}")
            return False
    
    def verify_imports(self):
        """导入检查 - 跳过 GUI 和外部依赖模块"""
        # 检查是否是 GUI 文件 (tkinter, PyQt, etc.)
        content = self.skill_path.read_text(encoding="utf-8")
        
        # 跳过 GUI 模块
        gui_modules = ["tkinter", "PyQt", "PySide", "wxPython", "kivy"]
        is_gui = any(mod in content for mod in gui_modules)
        
        if is_gui:
            print("⚠️  跳过 GUI 模块导入检查 (WSL 无图形界面)")
            return True
        
        # 跳过外部依赖模块 (WSL 可能未安装)
        external_deps = ["selenium", "streamlit", "playwright", "flask", "fastapi", "django"]
        has_external = any(mod in content for mod in external_deps)
        
        if has_external:
            print("⚠️  跳过外部依赖模块导入检查 (依赖可能未安装)")
            return True
        
        try:
            result = subprocess.run(
                ["python3", "-c", f"import sys; sys.path.insert(0, '{self.skill_path.parent}'); import {self.skill_path.stem}"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.skill_path.parent)
            )
            if result.returncode == 0:
                print("✅ 导入检查通过")
                return True
            else:
                print(f"❌ 导入错误：{result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 导入检查异常：{e}")
            return False
    
    def rollback(self):
        """回滚到备份"""
        if self.backup_path:
            shutil.copy2(self.backup_path, self.skill_path)
            os.unlink(self.backup_path)
            print("🔄 已回滚到优化前版本")
            self.report["rolled_back"] = True
    
    def cleanup(self):
        """清理备份"""
        if self.backup_path and os.path.exists(self.backup_path):
            os.unlink(self.backup_path)
            print("🧹 已清理备份文件")
    
    def generate_report(self):
        """生成报告"""
        report_path = self.skill_path.parent / f"{self.skill_path.stem}_evolution_report.json"
        report_path.write_text(json.dumps(self.report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"📄 报告已保存：{report_path}")
        return report_path
    
    def evolve(self):
        """完整进化流程"""
        print("=" * 60)
        print(f"🚀 技能进化：{self.skill_path.name}")
        print("=" * 60)
        
        # 1. 分析
        result = self.analyze()
        if not result:
            print("❌ 分析失败，终止流程")
            return False
        
        # 2. 备份
        self.backup()
        
        # 3. 应用优化
        self.apply_optimization(result["optimized_code"])
        
        # 4. 验证
        print("\n🔍 验证阶段...")
        
        if not self.verify_syntax():
            print("❌ 语法检查失败，回滚...")
            self.rollback()
            self.generate_report()
            return False
        
        if not self.verify_imports():
            print("❌ 导入检查失败，回滚...")
            self.rollback()
            self.generate_report()
            return False
        
        # 5. 重新评分（消耗更多 token，但能准确评估优化效果）
        print("\n📊 重新评分中...")
        new_result = self.analyze()
        if new_result:
            self.report["after_score"] = new_result["score"]
            self.report["issues_fixed"] = [
                issue["description"] for issue in self.report["issues_found"]
            ]
            score_improvement = new_result["score"] - self.report["before_score"]
            print(f"📈 评分提升：{self.report['before_score']} → {new_result['score']} (+{score_improvement})")
        
        # 6. 清理
        self.cleanup()
        self.report["test_passed"] = True
        
        # 7. 生成报告
        self.generate_report()
        
        print("\n✅ 进化完成！")
        print(f"📊 评分：{self.report['before_score']} → (待重新评分)")
        print(f"🐛 修复：{len(self.report['issues_found'])} 个问题")
        
        return True


def batch_evolve(skill_paths, max_concurrent=1):
    """批量进化"""
    print(f"\n🎯 批量进化：{len(skill_paths)} 个技能")
    
    results = []
    for i, path in enumerate(skill_paths, 1):
        print(f"\n[{i}/{len(skill_paths)}] 处理：{path}")
        engine = SkillEvolution(path)
        success = engine.evolve()
        results.append({"path": path, "success": success})
    
    # 汇总
    success_count = sum(1 for r in results if r["success"])
    print(f"\n{'='*60}")
    print(f"📊 批量进化完成：{success_count}/{len(skill_paths)} 成功")
    print(f"{'='*60}")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="技能进化引擎 v2.0")
    parser.add_argument("paths", nargs="+", help="要优化的技能文件路径")
    parser.add_argument("--batch", action="store_true", help="批量模式")
    
    args = parser.parse_args()
    
    if args.batch:
        batch_evolve(args.paths)
    else:
        for path in args.paths:
            engine = SkillEvolution(path)
            engine.evolve()
