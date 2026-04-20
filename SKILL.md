---
name: APIYI 图像生成插件
description: 支持文生图、图生图、多模型选择（GPT-4o Image、Flux Pro/Max、DALL-E 2/3 等）、多尺寸、多图生成的图像生成插件
---

# APIYI 图像生成插件

支持文生图、图生图、多模型选择（GPT-4o Image、Flux Pro/Max、DALL-E 2/3 等）、多尺寸、多图生成。

## 配置参数

- `provider`: 服务提供商 (coze 或 apiyi)
- `mode`: 生成模式 (text2img 或 img2img)
- `model`: 模型选择
- `size`: 图片尺寸
- `n`: 生成数量 (1-4)

## 使用方式

在对话中描述你想生成的图片，例如：
- "生成一只可爱的橘猫"
- "生成 1920x1080 的科幻城市风景"
- "把这张图改成赛博朋克风格"
