// 模拟Coze环境测试插件
import { handler } from './handler.js';

const testContext = {
  apiyi_api_key: "sk-Z39eHn58dCBzvt0R0b04Ef62C0404003Aa22E992E58f57D8"
};

async function runTest() {
  console.log("=== 测试文生图 ===");
  const result = await handler({
    input: {
      mode: "text2img",
      prompt: "一只可爱的橘猫在樱花树下打盹，日系插画风格",
      model: "gpt-4o-image",
      size: "1024x1024",
      n: 1
    },
    context: testContext
  });
  
  console.log(JSON.stringify(result, null, 2));
}

runTest().catch(console.error);
