from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('chatgpt_api_key'))

if messages == None:
    messages=[{
        "role": "user",
        "content": "Say this is a test",}]

def cgpt(ask):
    message = input(ask)
    messages.append({"role": "user", "content": message},)
    chat_completion = client.chat.completions.create(
        messages = messages,
        model="gpt-3.5-turbo-16k",)
    answer = chat_completion.choices[0].message.content
    messages.append({"role": "assistant", "content": answer})
    return answer