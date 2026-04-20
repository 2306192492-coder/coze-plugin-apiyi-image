/**
 * API易图像生成插件 v2.0 - Coze Handler
 * 
 * 功能：
 * - 文生图：输入文字描述，生成图片
 * - 图生图：上传原图+描述，智能编辑
 * - 多模型支持：GPT-4o Image、Nano Banana、Flux、DALL-E等
 * - 多尺寸支持：正方形、横版、竖版
 * - 多图生成：一次生成1-4张
 * 
 * 使用方法：
 * 1. 在Coze中创建Bot
 * 2. 添加此插件
 * 3. 配置API易API Key
 * 4. 选择模式调用
 */

export async function handler({ input, context }) {
  // 获取输入参数
  const { 
    mode = "text2img",
    prompt, 
    image_url,
    mask_url,
    model = "gpt-4o-image",
    size = "1024x1024",
    n = 1
  } = input;

  // 获取API Key
  const apiKey = context.apiyi_api_key || process.env.APIYI_API_KEY;

  // 参数校验
  if (!apiKey) {
    return {
      success: false,
      error: "请配置API易API Key"
    };
  }

  if (!prompt) {
    return {
      success: false,
      error: "请输入图像描述"
    };
  }

  if (mode === "img2img" && !image_url) {
    return {
      success: false,
      error: "图生图模式需要提供原图URL"
    };
  }

  // 数量限制
  const numImages = Math.min(Math.max(1, n), 4);

  try {
    let response;
    
    if (mode === "img2img") {
      // 图生图模式 - 使用编辑API
      response = await callImageEdit(apiKey, prompt, image_url, mask_url, model, size, numImages);
    } else {
      // 文生图模式
      response = await callImageGenerate(apiKey, prompt, model, size, numImages);
    }

    if (!response.ok) {
      const errorData = await response.json();
      return {
        success: false,
        error: `API调用失败: ${errorData.error?.message || response.statusText}`
      };
    }

    const data = await response.json();
    
    // 提取图片URL列表（处理b64_json或直接url）
    const imageUrls = data.data.map(item => {
      if (item.url) {
        return item.url;
      }
      if (item.b64_json) {
        // 返回base64数据URI格式
        return item.b64_json.startsWith('data:') ? item.b64_json : `data:image/png;base64,${item.b64_json}`;
      }
      return null;
    }).filter(url => url !== null);

    return {
      success: true,
      image_urls: imageUrls,
      model: model,
      size: size,
      count: imageUrls.length
    };

  } catch (error) {
    return {
      success: false,
      error: `请求异常: ${error.message}`
    };
  }
}

/**
 * 文生图API调用
 */
async function callImageGenerate(apiKey, prompt, model, size, n) {
  const baseUrl = "https://api.apiyi.com/v1/images/generations";
  
  // Flux系列使用aspect_ratio参数
  if (model.startsWith("black-forest-labs/")) {
    const aspectRatio = sizeToAspectRatio(size);
    return fetch(baseUrl, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: model,
        prompt: prompt,
        n: n,
        aspect_ratio: aspectRatio,
        prompt_upsampling: true
      })
    });
  }
  
  // DALL-E 3 特殊参数
  if (model === "dall-e-3") {
    return fetch(baseUrl, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: model,
        prompt: prompt,
        n: 1, // DALL-E 3 只支持单张
        size: size,
        quality: "hd",
        style: "vivid"
      })
    });
  }

  // 标准文生图调用
  return fetch(baseUrl, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: model,
      prompt: prompt,
      n: n,
      size: size
    })
  });
}

/**
 * 图生图/编辑API调用
 */
async function callImageEdit(apiKey, prompt, imageUrl, maskUrl, model, size, n) {
  const baseUrl = "https://api.apiyi.com/v1/images/edits";
  
  // Flux Max 编辑
  if (model === "black-forest-labs/flux-kontext-max") {
    return fetch(baseUrl, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: model,
        image: imageUrl,
        prompt: prompt,
        n: n
      })
    });
  }
  
  // DALL-E 2 编辑（支持遮罩）
  if (model === "dall-e-2") {
    const body = {
      model: model,
      image: imageUrl,
      prompt: prompt,
      n: n,
      size: size
    };
    if (maskUrl) {
      body.mask = maskUrl;
    }
    return fetch(baseUrl, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body)
    });
  }
  
  // GPT-Image-1 编辑
  if (model === "gpt-image-1") {
    return fetch(baseUrl, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: model,
        image: imageUrl,
        prompt: prompt,
        n: n,
        size: size
      })
    });
  }
  
  // 其他模型 - 尝试通用编辑接口
  return fetch(baseUrl, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: model,
      image: imageUrl,
      prompt: prompt,
      n: n,
      size: size
    })
  });
}

/**
 * 尺寸转宽高比（Flux系列用）
 */
function sizeToAspectRatio(size) {
  const ratioMap = {
    "1024x1024": "1:1",
    "1792x1024": "16:9",
    "1024x1792": "9:16",
    "1920x1080": "16:9",
    "1080x1920": "9:16",
    "1536x1024": "3:2",
    "1024x1536": "2:3"
  };
  return ratioMap[size] || "1:1";
}
