const apiKey = "sk-Z39eHn58dCBzvt0R0b04Ef62C0404003Aa22E992E58f57D8";

async function test() {
  const response = await fetch(
    "https://api.apiyi.com/v1/images/generations",
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: "gpt-4o-image",
        prompt: "一只可爱的橘猫在樱花树下打盹，日系插画风格",
        n: 1,
        size: "1024x1024"
      })
    }
  );
  
  console.log("Status:", response.status);
  const data = await response.json();
  console.log("Full response:", JSON.stringify(data, null, 2));
}

test().catch(console.error);
