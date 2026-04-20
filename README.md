# API易图像生成插件

Coze插件，调用API易平台的图像生成API，支持文生图和图生图编辑。

## 功能特性

- **文生图**：输入文字描述，生成高质量图片
- **图生图**：上传原图+描述，智能编辑（风格转换、局部修改）
- **多模型支持**：GPT-4o Image、Nano Banana Pro、Flux、DALL-E等
- **多尺寸支持**：正方形、横版、竖版
- **多图生成**：一次生成1-4张图片

## 支持模型

| 模型 | 文生图 | 图生图 | 特点 |
|------|--------|--------|------|
| GPT-4o Image | ✅ | ❌ | 💥 $0.01/张，性价比最高 |
| Nano Banana Pro | ✅ | ❌ | 谷歌模型，质量优秀 |
| GPT-Image-1 | ✅ | ✅ | OpenAI最新，功能全面 |
| Flux Pro | ✅ | ❌ | 专业级质量 |
| Flux Max | ✅ | ✅ | 最高质量，支持编辑 |
| DALL-E 3 | ✅ | ❌ | OpenAI官方，细节丰富 |
| DALL-E 2 | ✅ | ✅ | 经典模型，支持遮罩编辑 |

## 测试结果

```
=== 测试文生图 ===
{
  "success": true,
  "image_urls": ["data:image/png;base64,..."],
  "model": "gpt-4o-image",
  "size": "1024x1024",
  "count": 1
}
```

✅ 文生图功能正常
✅ 图生图功能已实现（待 API Key 测试）

### 1. 注册API易账号

访问 [API易平台](https://api.apiyi.com) 注册账号，获取API Key。

新用户赠送 $1.1 免费额度。

### 2. 在Coze中配置

1. 创建Bot
2. 添加插件 → 上传 `manifest.json` 和 `handler.js`
3. 配置凭证：填入API易API Key

### 3. 调用插件

**文生图示例：**
```
模式：文生图
描述：一只可爱的橘猫在樱花树下打盹，日系插画风格
模型：GPT-4o Image
尺寸：1024x1024
数量：1
```

**图生图示例：**
```
模式：图生图
描述：将这张照片转换为梵高星空风格
原图URL：https://example.com/photo.jpg
模型：Flux Max
```

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| mode | string | 否 | 生成模式：text2img（默认）/ img2img |
| prompt | string | 是 | 图像描述 |
| image_url | string | 图生图必填 | 原图URL |
| mask_url | string | 否 | 遮罩图URL（白色区域为编辑区） |
| model | string | 否 | 模型选择，默认 gpt-4o-image |
| size | string | 否 | 尺寸，默认 1024x1024 |
| n | number | 否 | 生成数量（1-4），默认 1 |

## 返回结果

**成功：**
```json
{
  "success": true,
  "image_urls": ["https://..."],
  "model": "gpt-4o-image",
  "size": "1024x1024",
  "count": 1
}
```

**失败：**
```json
{
  "success": false,
  "error": "错误信息"
}
```

## 悬赏计划

本插件为 [API易开源插件悬赏计划](https://help.apiyi.com/apiyi-open-source-plugin-bounty-coze-n8n-comfyui-2026.html) 提交作品。

## 许可证

MIT License

## 作者

公子
