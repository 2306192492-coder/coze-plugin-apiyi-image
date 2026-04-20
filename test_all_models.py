#!/usr/bin/env python3
"""
APIYI 图像生成模型全量测试脚本
测试所有支持的模型，生成测试报告
"""

import requests
import json
import time
from datetime import datetime

# 配置
API_KEY = "sk-Z39eHn58dCBzvt0R0b04Ef62C0404003Aa22E992E58f57D8"
BASE_URL = "https://api.apiyi.com/v1/images/generations"

# 测试提示词
TEST_PROMPT = "一只可爱的橘猫坐在窗台上，阳光洒在身上，高质量，细节丰富"

# 完整模型列表
MODELS = [
    # Nano Banana 系列 (Google Gemini)
    {"id": "gemini-3-pro-image", "name": "Nano Banana Pro", "group": "Nano Banana"},
    {"id": "gemini-3.1-flash-image-preview", "name": "Nano Banana 2", "group": "Nano Banana"},
    {"id": "gemini-2.5-flash-image-preview", "name": "Nano Banana", "group": "Nano Banana"},
    
    # GPT-Image 系列 (OpenAI)
    {"id": "chatgpt-image-1", "name": "GPT Image 1", "group": "GPT-Image"},
    {"id": "chatgpt-image-1-mini", "name": "GPT Image 1 Mini", "group": "GPT-Image"},
    
    # Flux 系列
    {"id": "flux-pro", "name": "Flux Pro", "group": "Flux"},
    {"id": "flux-dev", "name": "Flux Dev", "group": "Flux"},
    {"id": "flux-schnell", "name": "Flux Schnell", "group": "Flux"},
    {"id": "flux-kontext-pro", "name": "Flux Kontext Pro", "group": "Flux"},
    {"id": "flux-kontext-max", "name": "Flux Kontext Max", "group": "Flux"},
    
    # 其他顶级模型
    {"id": "seedream-5-0", "name": "SeeDream 5.0", "group": "Other"},
    {"id": "sora-image", "name": "Sora Image", "group": "Other"},
    {"id": "recraft-v3", "name": "Recraft V3", "group": "Other"},
    {"id": "ideogram-v3", "name": "Ideogram 3", "group": "Other"},
    {"id": "midjourney-v7", "name": "Midjourney v7", "group": "Other"},
    
    # DALL-E
    {"id": "dall-e-3", "name": "DALL-E 3", "group": "Other"},
]

def test_model(model_id, model_name, group):
    """测试单个模型"""
    print(f"\n{'='*60}")
    print(f"测试：{model_name} ({model_id}) - {group}")
    print(f"时间：{datetime.now().strftime('%H:%M:%S')}")
    
    # 构建请求体
    if group == "Flux":
        body = {
            "model": model_id,
            "prompt": TEST_PROMPT,
            "n": 1,
            "aspect_ratio": "1:1",
            "prompt_upsampling": True
        }
    elif model_id == "dall-e-3":
        body = {
            "model": model_id,
            "prompt": TEST_PROMPT,
            "n": 1,
            "size": "1024x1024",
            "quality": "standard",
            "style": "vivid"
        }
    elif group == "Nano Banana":
        body = {
            "model": model_id,
            "prompt": TEST_PROMPT,
            "n": 1,
            "size": "1024x1024",
            "generate_images": True
        }
    else:
        body = {
            "model": model_id,
            "prompt": TEST_PROMPT,
            "n": 1,
            "size": "1024x1024"
        }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        start_time = time.time()
        response = requests.post(BASE_URL, headers=headers, json=body, timeout=60)
        elapsed = time.time() - start_time
        
        print(f"耗时：{elapsed:.2f}s | 状态：{response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                img = data["data"][0]
                url = img.get("url", img.get("b64_json", "")[:50] + "..." if img.get("b64_json") else "N/A")
                print(f"✅ 成功！URL: {url}")
                return {"status": "success", "url": url, "time": elapsed}
            else:
                print(f"⚠️ 成功但无数据")
                return {"status": "empty", "time": elapsed}
        else:
            error = response.json() if response.text else {"text": response.text}
            print(f"❌ 失败：{error}")
            return {"status": "failed", "error": error, "code": response.status_code}
    
    except requests.exceptions.Timeout:
        print(f"❌ 超时")
        return {"status": "timeout"}
    except Exception as e:
        print(f"❌ 异常：{e}")
        return {"status": "exception", "error": str(e)}

def main():
    print("="*60)
    print("APIYI 图像生成模型全量测试")
    print(f"开始：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = []
    
    for i, model in enumerate(MODELS, 1):
        print(f"\n[{i}/{len(MODELS)}] ", end="")
        result = test_model(model["id"], model["name"], model["group"])
        result["model_id"] = model["id"]
        result["model_name"] = model["name"]
        result["group"] = model["group"]
        results.append(result)
        
        # 间隔 2 秒
        if i < len(MODELS):
            time.sleep(2)
    
    # 汇总
    print("\n\n" + "="*60)
    print("结果汇总")
    print("="*60)
    
    success = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] in ["failed", "timeout", "exception"])
    
    print(f"总计：{len(MODELS)} | ✅ 成功：{success} | ❌ 失败：{failed}")
    print("\n详细：")
    for r in results:
        icon = "✅" if r["status"] == "success" else "❌"
        print(f"{icon} {r['group']} - {r['model_name']}: {r['status']}")
    
    # 保存
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total": len(MODELS),
            "success": success,
            "failed": failed,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存：test_results.json")

if __name__ == "__main__":
    main()
