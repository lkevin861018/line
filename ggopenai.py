from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('chatgpt_api_key'))
# messages=[{'role':'system','content':'you are a black transgender non-binary person who grow up in ghetto area in down town san fransico. your political opinion is very left and believe that trump is really the neo nazi. you love rapping and all the blacks culture related behavior. you support abortion and believe female or woman have the right to choose what do they want to do with their body. you are very willing to share your political thought and not afaraid to correct people that have different opinion with you'}]
messages = [{'role':'system','content':'you are hentai,porn addictor,you have to use traditional Chinese reply'}]

def cgpt(ask, gen):
    global messages

    history = ""
    for msg in messages:
        history += f"{msg['role']}: {msg['content']}\n"

    full_input = history + f"user: {ask}\nassistant:"
    chat_completion = client.responses.create(
        model=gen,
        input=full_input
    )

    answer = chat_completion.output_text
    messages.append({"role": "user", "content": ask})
    messages.append({"role": "assistant", "content": answer})

    print(messages)
    return answer

def igpt(req):
    image_compleion = client.images.generate(
    # model="dall-e-3",
    model="gpt-image-1",
    prompt=req,
    size="auto",
    quality="auto",
    n=1,
    )

    image_url = image_compleion.data[0].url
    return image_url
