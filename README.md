# APIYI 图像生成 Coze 插件

> 🏆 **精品档提交作品** - 支持 16 个主流图像生成模型，5 个模型实测通过

Coze 标准结构插件，调用 APIYI 平台图像生成 API，支持文生图、图生图、多模型切换。

---

## 🎯 功能特性

- ✅ **文生图**：输入文字描述，生成高质量图片
- ✅ **图生图**：上传原图 + 描述，智能编辑（风格转换、局部修改）
- ✅ **16 个模型支持**：Nano Banana、GPT-Image、Flux、Midjourney 等
- ✅ **多尺寸支持**：正方形、横版 16:9、竖版 9:16
- ✅ **批量生成**：一次生成 1-4 张图片
- ✅ **6 个工作流模板**：电商/封面/头像/插画/编辑/壁纸

---

## 📊 支持模型

### ✅ 已实测通过（5 个）

| 模型 | 模型 ID | 文生图 | 图生图 | 特点 | 测试截图 |
|------|---------|--------|--------|------|----------|
| **Nano Banana** | `gemini-2.5-flash-image-preview` | ✅ | ❌ | 💰 $0.02/张，速度快 | [查看](screenshots/models/01_Nano_Banana/) |
| **Flux Dev** | `flux-dev` | ✅ | ❌ | 🎨 艺术表现力强 | [查看](screenshots/models/02_Flux_Dev/) |
| **Flux Kontext Pro** | `flux-kontext-pro` | ✅ | ✅ | ✂️ 图生图编辑 | [查看](screenshots/models/03_Flux_Kontext_Pro/) |
| **Flux Kontext Max** | `flux-kontext-max` | ✅ | ✅ | 🌟 高质量编辑 | [查看](screenshots/models/04_Flux_Kontext_Max/) |
| **Sora Image** | `sora-image` | ✅ | ❌ | 💰 $0.01/张，超低价 | [查看](screenshots/models/05_Sora_Image/) |

### ⏳ 代码支持（待开通分组）

| 模型 | 模型 ID | 状态 |
|------|---------|------|
| Nano Banana Pro | `gemini-3-pro-image` | 需 NanoBananaEnterprise 分组 |
| Nano Banana 2 | `gemini-3.1-flash-image-preview` | 需 NanoBananaEnterprise 分组 |
| GPT Image 1 | `chatgpt-image-1` | 需联系 APIYI 开通 |
| GPT Image 1 Mini | `chatgpt-image-1-mini` | 需联系 APIYI 开通 |
| Flux Pro | `flux-pro` | 需升级分组 |
| Flux Schnell | `flux-schnell` | 需升级分组 |
| SeeDream 5.0 | `seedream-5-0` | 需升级分组 |
| Recraft V3 | `recraft-v3` | 需 Premium 分组 |
| Ideogram 3 | `ideogram-v3` | 需 Premium 分组 |
| Midjourney v7 | `midjourney-v7` | 需 Premium 分组 |
| DALL-E 3 | `dall-e-3` | 需升级分组 |

---

## 🚀 快速开始

### 1. 注册 APIYI 账号

访问 [APIYI 平台](https://api.apiyi.com) 注册账号，获取 API Key。

新用户赠送 **$1.1 免费额度**，足够测试所有基础模型。

### 2. 在 Coze 中安装插件

#### 方式 A：使用已发布的技能（推荐）

1. 打开 [Coze 编程](https://code.coze.cn)
2. 搜索 `apiyi-image-gen` 或 `APIYI 图像生成`
3. 添加到你的 Bot 中
4. 配置凭证 `apiyi_key`：填入你的 APIYI API Key

#### 方式 B：手动上传技能包

1. 下载本仓库的 `.skill` 文件（或自行打包）
2. 在 Coze 中：技能 → 添加技能 → 自定义技能
3. 上传 ZIP 包（包含 `SKILL.md` + `scripts/image_gen.py`）
4. 配置凭证 `apiyi_key`：填入你的 APIYI API Key

> ⚠️ **注意**：本插件使用 **Coze 标准结构**（SKILL.md + Python 脚本），不是旧的 `manifest.json` + `handler.js` 格式。

### 3. 使用插件

在 Bot 对话中直接描述需求：

**文生图示例：**
```
生成一只可爱的橘猫，1024x1024，用 Nano Banana 模型
```

**图生图示例：**
```
把这张照片转成梵高风格 [上传图片]
使用 Flux Kontext Max 模型
```

**指定参数：**
```json
{
  "mode": "text2img",
  "model": "gemini-2.5-flash-image-preview",
  "prompt": "一只可爱的橘猫",
  "size": "1024x1024",
  "n": 2
}
```

---

## 📁 项目结构

```
coze-plugin-apiyi-image/
├── SKILL.md                    # Coze 技能说明（含 YAML frontmatter）
├── scripts/
│   └── image_gen.py           # 核心逻辑（Python）
├── screenshots/
│   └── models/                # 5 个模型实测截图
│       ├── 01_Nano_Banana/
│       ├── 02_Flux_Dev/
│       ├── 03_Flux_Kontext_Pro/
│       ├── 04_Flux_Kontext_Max/
│       └── 05_Sora_Image/
├── 工作流示例模板.md           # 6 个工作流模板
├── 模型测试报告.md             # 16 个模型测试结果
├── 模型支持列表.md             # 完整模型 ID 列表
├── test_all_models.py         # 批量测试脚本
└── README.md                  # 本文档
```

---

## 📊 测试结果

### 批量测试（16 个模型）

```bash
python3 test_all_models.py
```

**结果汇总：**
- 总计：16 个模型
- ✅ 成功：5 个 (31.25%)
- ❌ 待开通：11 个 (68.75%) - 需升级 API 分组

详细结果见：[模型测试报告.md](模型测试报告.md)

### 实测截图

每个成功模型的生成效果已保存在 `screenshots/models/` 文件夹：

- [Nano Banana 生成结果](screenshots/models/01_Nano_Banana/)
- [Flux Dev 生成结果](screenshots/models/02_Flux_Dev/)
- [Flux Kontext Pro 生成结果](screenshots/models/03_Flux_Kontext_Pro/)
- [Flux Kontext Max 生成结果](screenshots/models/04_Flux_Kontext_Max/)
- [Sora Image 生成结果](screenshots/models/05_Sora_Image/)

---

## 💡 工作流模板

已提供 6 个完整工作流模板，覆盖常见使用场景：

1. **电商产品图** - Nano Banana，批量生成，$0.08/4 张
2. **社交媒体封面** - Flux Kontext Pro，1920×1080 横版
3. **头像生成** - Sora Image，超低价，$0.02/2 张
4. **艺术插画** - Flux Dev，艺术表现力强
5. **图生图编辑** - Flux Kontext Max，高质量风格转换
6. **手机壁纸** - Nano Banana，1080×1920 竖版

详见：[工作流示例模板.md](工作流示例模板.md)

---

## 🔧 开发说明

### 凭证配置

在 Coze 中配置凭证：
- **凭证名称**：`apiyi_key`
- **类型**：API Key
- **域名**：`api.apiyi.com`

### 本地测试

```bash
# 安装依赖
pip install requests

# 运行测试
python3 test_all_models.py

# 生成实测截图
python3 generate_screenshots.py
```

### API 调用示例

```python
import requests

API_KEY = "sk-YOUR_API_KEY"
BASE_URL = "https://api.apiyi.com/v1/images/generations"

# Nano Banana 文生图
response = requests.post(
    BASE_URL,
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "model": "gemini-2.5-flash-image-preview",
        "prompt": "一只可爱的橘猫",
        "n": 1,
        "size": "1024x1024",
        "generate_images": True
    }
)

data = response.json()
print(data["data"][0]["url"])
```

---

## 🏆 Bounty 提交

**提交类别**：精品档（¥1000-3000 + ¥2000-5000 额度）

**提交材料**：
- ✅ GitHub 公开仓库（MIT 协议）
- ✅ 16 个模型支持（5 个实测通过）
- ✅ 文生图 + 图生图功能
- ✅ 6 个工作流模板
- ✅ 完整测试报告
- ✅ Coze 官方校验通过

**提交链接**：
- GitHub: https://github.com/2306192492-coder/coze-plugin-apiyi-image
- APIYI 悬赏页面：https://help.apiyi.com/apiyi-open-source-plugin-bounty-coze-n8n-comfyui-2026.html

---

## 📝 更新日志

### v2.0 (2026-04-20)
- 🎉 升级为 Coze 标准结构（SKILL.md + Python 脚本）
- ✅ 支持 16 个主流图像生成模型
- ✅ 新增 5 个模型实测截图
- ✅ 新增 6 个工作流模板
- ✅ 新增批量测试脚本
- ✅ 完善文档和测试报告

### v1.0 (2026-04-19)
- 初始版本（manifest.json + handler.js）
- 支持基础文生图功能

---

## 📞 联系方式

- **GitHub**: [@2306192492-coder](https://github.com/2306192492-coder)
- **APIYI**: [api.apiyi.com](https://api.apiyi.com)
- **Coze**: [code.coze.cn](https://code.coze.cn)

---

**MIT License** © 2026 APIYI Plugin Contributors
