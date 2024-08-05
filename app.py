import requests
from flask import Flask, request, Response, jsonify
from openai import OpenAI
import os
from prompt import create_prompt, update_response_list
from step_count import count_steps

app = Flask(__name__)

telegram_bot_token = os.environ.get('BOT_TOKEN')
OPEN_AI_KEY = os.environ.get('OPEN_AI_KEY')
# model = genai.GenerativeModel('gemini-pro')
system_instruction = 'You are a health assistant chatbot named Guardian Angel. You offer meaningful and accurate insight on health data in a concise and formal manner. You can reply in multiple languages if prompted'
client = OpenAI(
    api_key= OPEN_AI_KEY,
)
last_prompt = 'Empty'

def generate_content(prompt):
  completion = client.chat.completions.create(
    model="gpt-4o",
    # temperature = 0.2,
    max_tokens = 45,
    messages=[
      {"role": "user", "content": prompt}
    ]
    # optionally, add system instruction here
  )
  return completion.choices[0].message

def generate_answer(question):
    try:
        response = generate_content(question)
        print(response)
        return response.content
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
    # print(response.text)
    return response

@app.route('/api', methods=['POST'])
def post_data():
    try:
        data = request.get_json()
        print("Received JSON data:")
        # print(data)
        # print(type(data['chat_id']))
        # print(data['data'])
        steps = count_steps(data['data'])
        # print(steps)
        prompt = f"I took {steps} steps today. Give me an encouraging message with that number"
        answer = generate_answer(prompt)
        # print(answer)
        send_message_telegram(data['chat_id'], answer)
        # print(data['user_id'])
        # print(data['health_data'])
        # chat_id, uid, prompt = create_prompt(data['user_id'], data['health_data'])
        # # last_prompt = prompt
        # send_message_telegram(chat_id, prompt)
        # answer = generate_answer(eval(chat_id), prompt)
        # print(chat_id, answer)
        # send_message_telegram(chat_id, answer)
        # update_response_list(uid, answer)
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
            elif incoming_que.strip() == '/start':
                start_msg = "Hi there! I'm Guardian Angel, your AI companion for health and wellness. To get started, type '/instructions' for a helping hand"
                send_message_telegram(chat_id, start_msg)
            elif incoming_que.strip() == '/instructions':
                instructions_msg = "**Welcome to Guardian Angel!**\n\nI'm your AI health companion, here to help you stay on top of your well-being.\n\nTo get started, sign up at [this url](https://stingray-app-rdd32.ondigitalocean.app/signup) and create an account. \n\nYou'll need your Chat ID to complete signup. Enter **/chatid** in this chat to retrieve your unique ID.\n\nDuring signup on the website, enter the User ID programmed into your health band to link it with Guardian Angel.\n\nHappy health tracking!"
                send_message_telegram(chat_id, instructions_msg)
            elif incoming_que.strip() == '/lastprompt':
                send_message_telegram(chat_id, last_prompt)
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
