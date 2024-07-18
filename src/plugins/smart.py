#smart.py
import requests as requests

# 在这里配置您在本站的API_KEY
api_key = "sk-z9Qay5X01B1f34422D87T3BlbKFJ0733dC6a4cC04123a090"

headers = {
    "Authorization": 'Bearer ' + api_key,
}



def answer(message_list = list):
    params = {
        "messages": message_list,
        # 如果需要切换模型，在这里修改
        "model": 'gpt-3.5-turbo'
    }
    response = requests.post(
        "https://aigptx.top/v1/chat/completions",
        headers=headers,
        json=params,
        stream=False
    )
    res = response.json()
    print(res)
    res_content = res['choices'][0]['message']['content']
    print(res_content)
    return res_content