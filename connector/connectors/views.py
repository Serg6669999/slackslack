from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json
import requests


@csrf_exempt
def slack_chatme(request):
    """example request slack = {
        "token": "one-long-verification-token",
        "team_id": "T061EG9R6",
        "api_app_id": "A0PNCHHK2",
        "event": {
            "type": "message",
            "channel": "D024BE91L",
            "user": "U2147483697",
            "text": "Hello hello can you hear me?",
            "ts": "1355517523.000005",
            "event_ts": "1355517523.000005",
            "channel_type": "im"
        },
        "type": "event_callback",
        "authed_teams": [
            "T061EG9R6"
        ],
        "event_id": "Ev0PV52K21",
        "event_time": 1355517523
    }
    example_response_chatme = {{
                                "has_answer": true,
                                "messages": [{
                                    "text": "text_list"
                                }]
                            }
    """
    if request.method == 'POST':
        data_dict = to_extract_data_dict_from_request(request)
        mybe_challenge = data_dict.get('challenge')
        if mybe_challenge:  # проверяем пришла ли авторизация
            response_dict = {'challenge': mybe_challenge}
            response = JsonResponse(response_dict)
        elif data_dict['event'].get('username'):  # бот отправляет событие также после прихода к нему сообщения от
            # сервиса, а не только от сообщения пользователя, это событие не обрабатываем
            response = HttpResponse(status=204)
        else:  # обрабатываем событие - в чат skack пришло сообщение от пользователя
            message_to_the_slack_is_sent_to_url = 'https://slack.com/api/chat.postMessage'
            message_to_the_chatme_is_sent_to_url = 'https://admin.chatme.ai/connector/webim/webim_message/' \
                                                   'sH0knsK1jJt8YPqV-iU04A/bot_api_webhook'
            header_slack = {
                "Authorization": "Bearer xoxb-870665549127-863766108834-BcKZnwkn3JSMSsN8UFrKuHLn"}
            header_chatme = {"Content-type": "application/json"}
            event = data_dict['event']
            channel = event['channel']
            text_from_slack = event['text']
            body_request_for_chatme = {"event": "new_message",
                                       "chat": {"id": 1},
                                       "text": text_from_slack
                                       }
            response_chatme = send_request(message_to_the_chatme_is_sent_to_url, body_request_for_chatme,
                                           header_chatme)
            print('response_chatme = ', response_chatme.json())
            data_dict_from_chatme = to_extract_data_dict_from_response(response_chatme)
            text_from_chatme = to_extract_text_from_data_dict_from_chatme(data_dict_from_chatme)
            body_request_for_slack = {"channel": channel,
                                      "text": text_from_chatme,
                                      }
            response_slack = send_request(message_to_the_slack_is_sent_to_url, body_request_for_slack, header_slack)
            print('response_slack = ', response_slack.json())
            response = HttpResponse(status=204)
        return response


def to_extract_data_dict_from_request(request):
    data = request.body.decode('utf-8')
    data_dict = json.loads(data)
    return data_dict


def to_extract_data_dict_from_response(response):
    dict_ = response.json()
    return dict_


def send_request(url: str, body_request: dict, header):
    request = requests.post(url, json=body_request, headers=header)
    return request


def to_extract_text_from_data_dict_from_chatme(data_dict_from_chatme):
    messages = data_dict_from_chatme['messages']
    dict_messages = messages[0]
    text_ = dict_messages['text']
    return text_
