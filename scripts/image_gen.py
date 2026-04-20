"""
APIYI 图像生成插件 - Python 脚本
支持文生图、图生图、多模型、多尺寸、多图生成
"""

import requests
import os
from typing import Optional, List, Dict, Any


def main(params: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    主函数：处理图像生成请求
    
    Args:
        params: 输入参数
            - mode: 生成模式 (text2img 或 img2img)
            - prompt: 图像描述
            - image_url: 原图 URL（图生图模式需要）
            - mask_url: 遮罩图 URL（可选）
            - model: 模型名称
            - size: 图片尺寸
            - n: 生成数量 (1-4)
        context: Coze 上下文对象，用于获取凭证
    
    Returns:
        包含生成结果的字典
    """
    # 获取输入参数
    mode = params.get("mode", "text2img")
    prompt = params.get("prompt", "")
    image_url = params.get("image_url", "")
    mask_url = params.get("mask_url", "")
    model = params.get("model", "gpt-4o-image")
    size = params.get("size", "1024x1024")
    n = params.get("n", 1)
    
    # 获取 API Key（从 Coze 凭证系统）
    api_key = getattr(context, 'apiyi_api_key', None) or os.getenv('APIYI_API_KEY')
    
    # 参数校验
    if not api_key:
        return {
            "success": False,
            "error": "请配置 API 易 API Key"
        }
    
    if not prompt:
        return {
            "success": False,
            "error": "请输入图像描述"
        }
    
    if mode == "img2img" and not image_url:
        return {
            "success": False,
            "error": "图生图模式需要提供原图 URL"
        }
    
    # 数量限制 (1-4)
    num_images = max(1, min(n, 4))
    
    try:
        if mode == "img2img":
            # 图生图模式
            response = call_image_edit(
                api_key, prompt, image_url, mask_url, model, size, num_images
            )
        else:
            # 文生图模式
            response = call_image_generate(
                api_key, prompt, model, size, num_images
            )
        
        if not response.ok:
            error_data = response.json()
            return {
                "success": False,
                "error": f"API 调用失败：{error_data.get('error', {}).get('message', response.text)}"
            }
        
        data = response.json()
        
        # 提取图片 URL 列表
        image_urls = []
        for item in data.get("data", []):
            if "url" in item:
                image_urls.append(item["url"])
            elif "b64_json" in item:
                b64 = item["b64_json"]
                if not b64.startswith("data:"):
                    b64 = f"data:image/png;base64,{b64}"
                image_urls.append(b64)
        
        return {
            "success": True,
            "image_urls": image_urls,
            "model": model,
            "size": size,
            "count": len(image_urls)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"请求异常：{str(e)}"
        }


def call_image_generate(
    api_key: str,
    prompt: str,
    model: str,
    size: str,
    n: int
) -> requests.Response:
    """文生图 API 调用"""
    base_url = "https://api.apiyi.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Flux 系列使用 aspect_ratio
    if model.startswith("black-forest-labs/"):
        aspect_ratio = size_to_aspect_ratio(size)
        body = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "aspect_ratio": aspect_ratio,
            "prompt_upsampling": True
        }
    # DALL-E 3 特殊参数
    elif model == "dall-e-3":
        body = {
            "model": model,
            "prompt": prompt,
            "n": 1,  # DALL-E 3 只支持单张
            "size": size,
            "quality": "hd",
            "style": "vivid"
        }
    # 标准调用
    else:
        body = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size
        }
    
    return requests.post(base_url, headers=headers, json=body)


def call_image_edit(
    api_key: str,
    prompt: str,
    image_url: str,
    mask_url: str,
    model: str,
    size: str,
    n: int
) -> requests.Response:
    """图生图/编辑 API 调用"""
    base_url = "https://api.apiyi.com/v1/images/edits"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Flux Max 编辑
    if model == "black-forest-labs/flux-kontext-max":
        body = {
            "model": model,
            "image": image_url,
            "prompt": prompt,
            "n": n
        }
    # DALL-E 2 编辑（支持遮罩）
    elif model == "dall-e-2":
        body = {
            "model": model,
            "image": image_url,
            "prompt": prompt,
            "n": n,
            "size": size
        }
        if mask_url:
            body["mask"] = mask_url
    # GPT-Image-1 编辑
    elif model == "gpt-image-1":
        body = {
            "model": model,
            "image": image_url,
            "prompt": prompt,
            "n": n,
            "size": size
        }
    # 通用编辑接口
    else:
        body = {
            "model": model,
            "image": image_url,
            "prompt": prompt,
            "n": n,
            "size": size
        }
    
    return requests.post(base_url, headers=headers, json=body)


def size_to_aspect_ratio(size: str) -> str:
    """尺寸转宽高比（Flux 系列用）"""
    ratio_map = {
        "1024x1024": "1:1",
        "1792x1024": "16:9",
        "1024x1792": "9:16",
        "1920x1080": "16:9",
        "1080x1920": "9:16",
        "1536x1024": "3:2",
        "1024x1536": "2:3"
    }
    return ratio_map.get(size, "1:1")
