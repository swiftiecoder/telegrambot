import requests
from flask import Flask, request, Response, jsonify
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os
from prompt import create_prompt, update_response_list

app = Flask(__name__)

telegram_bot_token = os.environ.get('BOT_TOKEN')
bot_username = os.environ.get('BOT_USERNAME')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
# model = genai.GenerativeModel('gemini-pro')
model = genai.GenerativeModel('gemini-1.5-pro-latest', system_instruction = 'You are a health assistant chatbot named Guardian Angel. You offer meaningful and accurate insight on health data in a concise and converstional manner. You can reply in multiple languages if prompted')
chats = {}
global last_prompt = 'Empty'

def chat_length(chat_id):
    if chat_id in chats.keys():
        return len(chats[chat_id].history)//2
    else:
        return -1
        
def chat_exists(chat_id):
    if chat_id in chats.keys():
        return True
    else:
        return False
        
def create_chat(chat_id):
    if chat_id == -1:
        return
    if chat_exists(chat_id):
        return
    else:
        chats[chat_id] = model.start_chat(history=[])

def generate_answer(chat_id, question):
    try:
        if not chat_exists(chat_id):
            create_chat(chat_id)
        response = chats[chat_id].send_message(question, safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        })
        print(response)
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

@app.route('/api', methods=['POST'])
def post_data():
    try:
        data = request.get_json()
        print("Received JSON data:")
        # print(data['user_id'])
        # print(data['health_data'])
        chat_id, uid, prompt = create_prompt(data['user_id'], data['health_data'])
        chat_id = int(chat_id)
        last_prompt = prompt
        print(last_prompt, prompt)
        answer = generate_answer(chat_id, prompt)
        print(chat_id, answer)
        send_message_telegram(chat_id, answer)
        update_response_list(uid, answer)
    
        return jsonify({'message': 'Data received successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        chat_id, incoming_que = message_parser(msg)
        if chat_id != -1:
            if incoming_que.strip() == '/chatid':
                send_message_telegram(chat_id, f'Your chat ID is: {chat_id}')
            elif incoming_que.strip() == '/chatlen':
                send_message_telegram(chat_id, f'Your chat length is: {chat_length(chat_id)}')
            elif incoming_que.strip() == '/start':
                create_chat(chat_id)
                start_msg = "Hi there! I'm Guardian Angel, your AI companion for health and wellness. To get started, type '/instructions' for a helping hand"
                send_message_telegram(chat_id, start_msg)
            elif incoming_que.strip() == '/instructions':
                instructions_msg = "**Welcome to Guardian Angel!**\n\nI'm your AI health companion, here to help you stay on top of your well-being.\n\nTo get started, sign up at [this url](https://stingray-app-rdd32.ondigitalocean.app/signup) and create an account. \n\nYou'll need your Chat ID to complete signup. Enter **/chatid** in this chat to retrieve your unique ID.\n\nDuring signup on the website, enter the User ID programmed into your health band to link it with Guardian Angel.\n\nHappy health tracking!"
                send_message_telegram(chat_id, instructions_msg)
            elif incoming_que.strip() == '/numusers':
                send_message_telegram(chat_id, f'There are {len(chats)} users')
            elif incoming_que.strip() == '/removeme':
                del chats[chat_id]
                send_message_telegram(chat_id, 'You have been removed')
            elif incoming_que.strip() == '/removeall':
                chats.clear()
            elif incoming_que.strip() == '/lastprompt':
                send_message_telegram(chat_id, last_prompt)
            elif incoming_que.strip() == '/chathistory':
                try:
                    print(chats[chat_id].history)
                    send_message_telegram(chat_id, chats[chat_id].history)
                except:
                    send_message_telegram(chat_id, "Something went wrong")
            elif incoming_que.strip() == '/chatdic':
                try:
                    print(chats)
                    send_message_telegram(chat_id, chats)
                except:
                    send_message_telegram(chat_id, "Something went wrong")
            elif incoming_que == '__NONE__':
                send_message_telegram(chat_id, 'Sorry, I can only interact with text right now :(')
            else:
                answer = generate_answer(chat_id, incoming_que)
                send_message_telegram(chat_id, answer)
        return Response('ok', status=200)
    else:
        # print(telegram_bot_token, GOOGLE_API_KEY)
        return "<h1>GET Request Made</h1>"


if __name__ == '__main__':
    app.run()
