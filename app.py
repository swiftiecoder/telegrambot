import requests
from flask import Flask, request, Response
import google.generativeai as genai

app = Flask(__name__)

telegram_bot_token = '7109406430:AAFcr3QHimeRd5j4DJztzo5bka5YKGrv8Lo'
bot_username = '@angel_medbot'
GOOGLE_API_KEY = 'AIzaSyAsK8D9rop1CV9487Rnkxs1r1zVt3qmtyQ'
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def generate_answer(question):
    chat = model.start_chat(history=[])
    response = chat.send_message(question)
    return response.text

def message_parser(message):
    chat_id = message['message']['chat']['id']
    text = message['message']['text']
    print("Chat ID: ", chat_id)
    print("Message: ", text)
    return chat_id, text

def send_message_telegram(chat_id, text):
    url = f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, json=payload)
    return response

# add route for esp to send data which is stored in firebase/local list idk

# add logic to get chat id for this data from the firebase db

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        chat_id, incoming_que = message_parser(msg)
        if incoming_que.strip() == '/chatid':
            send_message_telegram(chat_id, f'Your chat ID is: {chat_id}')
        else:
            answer = generate_answer(incoming_que)
            send_message_telegram(chat_id, answer)
        return Response('ok', status=200)
    else:
        return "<h1>Something went wrong</h1>"
