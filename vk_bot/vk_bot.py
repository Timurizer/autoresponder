import vk_api
from answerer import *
import time

confirmation_token = 'c0911454'
token = '8f927fb9b8da367175b388067c25c38e6a6134088b920e32560d1013a9ba118ffc2cab7df987a6bda781a'
vk = vk_api.VkApi(token=token)

values = {'out': 0, 'count': 100, 'time_offset': 60}


def write_msg(user_id, s):
    vk.method('messages.send', {'user_id': user_id, 'message': s})


while True:
    response = vk.method('messages.get', values)
    if response['items']:
        values['last_message_id'] = response['items'][0]['id']
    for item in response['items']:
        if item['body'] == 'привет':
            write_msg(item[u'user_id'], u'Тимур Якупов')
        else:
            question = item['body']
            data = answer(question)
            result = ""
            for i in data:
                result += "Question: " + i[0] + "\nAnswer: " + i[1] + "Confidence: " + str(i[2]) + "\n"
                result += "-" * 15 + "\n"
            write_msg(item[u'user_id'], result)
    time.sleep(1)
