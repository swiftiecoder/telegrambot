import requests
import json
import os
import pyrebase

config = {
	"apiKey": os.environ.get('FIREBASE_API_KEY'),
    "authDomain": "sb-flask.firebaseapp.com",
    "databaseURL": "https://sb-flask-default-rtdb.firebaseio.com",
    "projectId": "sb-flask",
    "storageBucket": "sb-flask.appspot.com",
    "messagingSenderId": "537358433568",
    "appId": "1:537358433568:web:a0425f0a4445bafcd7eb45"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

def read_health_data(file_path):
    # Read health readings from a JSON file
    with open(file_path, 'r') as file:
        health_data = json.load(file)
    return health_data

def create_prompt(user_id, health_data):
    # Construct the URL to access the user's data
    data = db.child("users").order_by_child("user id").equal_to(user_id).get()
    uid = user_info = next(iter(dict(data.val()).keys()))
    user_info = next(iter(dict(data.val()).values()))
    if user_info:
        # Construct the prompt string using user_info and health_data
        prompt = f"User ID: {user_id}\n"
        prompt += f"Age: {user_info['age']}, Weight: {user_info['weight']}, Height: {user_info['height']}\n"
        prompt += f"Blood Sugar: {user_info['blood_sugar']}, Blood Pressure: {user_info['blood_pressure']}, Heart Disease History: {user_info['heart_history']}\n"
        prompt += f"Temperature Readings: {health_data['temperatures']}\n"
        prompt += f"Heart Rate Readings: {health_data['heart_rates']}\n"
        prompt += f"Respiratory Index Readings: {health_data['respiratory_indices']}\n"
        prompt += f"Oxygen Level Readings: {health_data['oxygen_levels']}\n"
        
        # Include the recent responses in the prompt
        responses = user_info.get('responses', [])
        prompt += f"Recent Responses: {responses}\n"
	addtional = {user_info['additional_info']}
        prompt += f"Some additional information about the user:{addtional}\n"
        prompt += "You are a medical chatbot whose job is to receive patient health information and detect issues. Please diagnose any potential illnesses or anomolous activity based on the readings provided as if you are a medical professional. Provide meaningful insight into the user's health. Be conversational and concise"
    
    else:
            return f"No user info found for user ID: {user_id}"
    
    return user_info['chat_id'], uid, prompt


def update_response_list(user_id, new_response):
    # Construct the URL to access the user's responses field
    url = f'https://sb-flask-default-rtdb.firebaseio.com/users/{user_id}/responses.json'
    
    # Send a GET request to fetch the current response list
    get_response = requests.get(url)
    
    if get_response.status_code == 200:
        response_list = get_response.json() or []  # Ensure we have a list
        
        # Update the response list
        if len(response_list) >= 5:
            response_list.pop(0)
        response_list.append(new_response)
        
        # Send a PUT request to update the response list
        put_response = requests.put(url, json.dumps(response_list))
        
        if put_response.status_code in [200, 204]:
            return "Response list updated."
        else:
            return f"Failed to update data: {put_response.status_code}"
    else:
        return f"Failed to retrieve data: {get_response.status_code}"

# Example usage:

if __name__ == '__main__':
    # First, read health data from the JSON file
    health_data = read_health_data('dummy_readings.json')
    print("JSON file contents:", health_data)

    # Then, use this data along with the user ID to create a prompt
    prompt = create_prompt('tYX9kkq774XOFFRL0Yx3R32IJUD2', health_data)
    print(prompt)

    # checking see if responses are being appended in the DB

    update_response_list('tYX9kkq774XOFFRL0Yx3R32IJUD2', 'response0')
    update_response_list('tYX9kkq774XOFFRL0Yx3R32IJUD2', 'response2')
    update_response_list('tYX9kkq774XOFFRL0Yx3R32IJUD2', 'response3')
    update_response_list('tYX9kkq774XOFFRL0Yx3R32IJUD2', 'response4')
    update_response_list('tYX9kkq774XOFFRL0Yx3R32IJUD2', 'response5')

