import requests
from flask import Flask, request, Response
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
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
    try:
        response = chat.send_message(question, safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        })
        return response.text
    except:
        return "Something went wrong generating the response"

def message_parser(message):
    try:
        chat_id = message['message']['chat']['id']
        try:
            text = message['message']['text']
        except:
            text = '__NONE__'
    except:
        chat_id = -1
        text = '__NONE__'
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
        if chat_id != -1:
            if incoming_que.strip() == '/chatid':
                send_message_telegram(chat_id, f'Your chat ID is: {chat_id}')
            elif incoming_que.strip() == '/start':
                start_msg = "Hi there! I'm Guardian Angel, your AI companion for health and wellness. To get started, type '/instructions' for a helping hand"
                send_message_telegram(chat_id, start_msg)
            elif incoming_que.strip() == '/instructions':
                instructions_msg = "**Welcome to Guardian Angel!**\n\nI'm your AI health companion, here to help you stay on top of your well-being.\n\nTo get started, sign up at [this url](https://stingray-app-rdd32.ondigitalocean.app/signup) and create an account. \n\nYou'll need your Chat ID to complete signup. Enter **/chatid** in this chat to retrieve your unique ID.\n\nDuring signup on the website, enter the User ID programmed into your health band to link it with Guardian Angel.\n\nHappy health tracking!"
                send_message_telegram(chat_id, instructions_msg)
            elif incoming_que == '__NONE__':
                send_message_telegram(chat_id, 'Sorry, I can only interact with text right now :(')
            else:
                answer = generate_answer(incoming_que)
                send_message_telegram(chat_id, answer)
        return Response('ok', status=200)
    else:
        print(telegram_bot_token, GOOGLE_API_KEY)
        return "<h1>GET Request Made</h1>"


if __name__ == '__main__':
    app.run()
