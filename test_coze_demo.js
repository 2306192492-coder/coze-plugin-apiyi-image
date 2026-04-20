// Coze 插件测试脚本 - 模拟 Coze 环境调用 APIYI 图像生成插件
// 用法：node test_coze_demo.js

const handler = require('./handler.js');

// 你的 API Key
const API_KEY = 'sk-Z39eHn58dCBzvt0R0b04Ef62C0404003Aa22E992E58f57D8';

// 测试场景 1: 文生图 - 可爱猫咪
async function testText2Img() {
  console.log('🎨 测试 1: 文生图 - 可爱猫咪');
  console.log('提示词：一只可爱的橘猫在樱花树下打盹，日系插画风格，柔和光线\n');

  const cozeParams = {
    input: {
      mode: 'text2img',
      prompt: '一只可爱的橘猫在樱花树下打盹，日系插画风格，柔和光线',
      model: 'gpt-4o-image',
      size: '1024x1024',
      n: 1
    },
    context: {
      apiyi_api_key: API_KEY
    }
  };

  try {
    const result = await handler.handler(cozeParams);
    console.log('✅ 生成成功！');
    console.log('返回结果:', JSON.stringify(result, null, 2));
    
    if (result.image_urls && result.image_urls[0]) {
      console.log('\n📸 图片预览:');
      console.log('   将图片 URL 复制到浏览器查看');
      console.log('   URL:', result.image_urls[0].substring(0, 100) + '...');
    }
    return result;
  } catch (error) {
    console.error('❌ 生成失败:', error.message);
    return null;
  }
}

// 测试场景 2: 文生图 - 赛博朋克城市
async function testCyberpunk() {
  console.log('\n🌃 测试 2: 文生图 - 赛博朋克城市');
  console.log('提示词：赛博朋克风格未来城市，霓虹灯闪烁，雨夜，高楼林立，飞行汽车\n');

  const cozeParams = {
    input: {
      mode: 'text2img',
      prompt: '赛博朋克风格未来城市，霓虹灯闪烁，雨夜，高楼林立，飞行汽车',
      model: 'gpt-4o-image',
      size: '1920x1080',
      n: 1
    },
    context: {
      apiyi_api_key: API_KEY
    }
  };

  try {
    const result = await handler.handler(cozeParams);
    console.log('✅ 生成成功！');
    console.log('返回结果:', JSON.stringify(result, null, 2));
    return result;
  } catch (error) {
    console.error('❌ 生成失败:', error.message);
    return null;
  }
}

// 测试场景 3: 文生图 - 古风仙侠
async function testFantasy() {
  console.log('\n⚔️ 测试 3: 文生图 - 古风仙侠');
  console.log('提示词：中国古风仙侠，白衣剑客站在山顶，云海缭绕，夕阳西下，水墨画风格\n');

  const cozeParams = {
    input: {
      mode: 'text2img',
      prompt: '中国古风仙侠，白衣剑客站在山顶，云海缭绕，夕阳西下，水墨画风格',
      model: 'gemini-3-pro-image',
      size: '1080x1920',
      n: 1
    },
    context: {
      apiyi_api_key: API_KEY
    }
  };

  try {
    const result = await handler.handler(cozeParams);
    console.log('✅ 生成成功！');
    console.log('返回结果:', JSON.stringify(result, null, 2));
    return result;
  } catch (error) {
    console.error('❌ 生成失败:', error.message);
    return null;
  }
}

// 主函数
async function main() {
  console.log('═══════════════════════════════════════════════');
  console.log('   APIYI Coze 插件 - 运行效果演示');
  console.log('═══════════════════════════════════════════════\n');

  // 运行测试
  await testText2Img();
  await testCyberpunk();
  await testFantasy();

  console.log('\n═══════════════════════════════════════════════');
  console.log('✅ 所有测试完成！');
  console.log('═══════════════════════════════════════════════');
  console.log('\n📸 下一步操作:');
  console.log('1. 在 Coze 中创建 Bot');
  console.log('2. 上传 manifest.json 和 handler.js');
  console.log('3. 配置 API Key 凭证');
  console.log('4. 在对话框输入: "生成一只可爱的猫咪"');
  console.log('5. 截图保存运行效果');
}

main();
