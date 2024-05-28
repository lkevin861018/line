from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('chatgpt_api_key'))
messages=[]

def cgpt(ask):
    messages.append({"role": "user", "content": ask},)
    chat_completion = client.chat.completions.create(
        messages = messages,
        # model="gpt-3.5-turbo-16k",)
        model="gpt-4o-2024-05-13",)
    answer = chat_completion.choices[0].message.content
    messages.append({"role": "assistant", "content": answer})
    return answer

def igpt(req):
    image_compleion = client.images.generate(
    model="dall-e-3",
    prompt=req,
    size="1024x1024",
    quality="standard",
    n=1,
    )

    image_url = image_compleion.data[0].url
    return image_url