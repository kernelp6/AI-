# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI

client = OpenAI(  api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[
        {"role": "system", "content": "你是一个可爱的ai助理，你的名字叫ptf的小助理，请你用温柔可爱的语气回答用户问题"},
        {"role": "user", "content": "你是谁，你能做什么？"},
    ],
    stream=False,

)

print(response.choices[0].message.content)