import requests
from flask import Flask, request, Response
import google.generativeai as genai
import os

app = Flask(__name__)

telegram_bot_token = os.environ.get('BOT_TOKEN')
bot_username = os.environ.get('BOT_USERNAME')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
no_text = False
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

def generate_answer(question):
    response = chat.send_message(question)
    return response.text

def message_parser(message):
    chat_id = message['message']['chat']['id']
    try:
        text = message['message']['text']
    except:
        text = 'NONE'
    print("Chat ID: ", chat_id)
    print("Message: ", text)
    return chat_id, text

def send_message_telegram(chat_id, text):
    url = f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode' : 'Markdown'
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
        elif no_text:
            no_text = False
            send_message_telegram(chat_id, 'Sorry, I can only interact with text right now :(')
        else:
            answer = generate_answer(incoming_que)
            send_message_telegram(chat_id, answer)
        return Response('ok', status=200)
    else:
        return "<h1>GET Request Made</h1>"


if __name__ == '__main__':
    app.run()
