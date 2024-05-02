from flask import Flask, request, jsonify
from datetime import datetime
import requests
import json
import logging
import pandas as pd
import mysql.connector
VERSION="v19.0"
PHONE_NUMBER_ID="271322246064973"
reciepent="+917010922948"
verify_token ="12345"

# Set up WhatsApp Business API client
whatsapp_url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"

#auth = ('your-username', 'your-password')
access_token = "EAALJ6vKZAwAQBO2w7ExxZALNpQd5Tvlz1n2d0DeAY5PbPPtOKZBLRo09OWJPbvut1ltCq1YMHBVMjo1L4Smi0lQfA7qlcIdDfUndKnPMlQqdH1dI1dnUL8zart1meiOrJX9w2453QNF2AOmLLVv4azTkAwr037bSP35CpQ7qDp94aFU2eIIPB826Ml3Mi6EeAMKP10KgWZCnhHXyJ7YZD"


# Read data from Excel file
df = pd.read_excel('E:\\users.xlsx')
recipients = df['Phone'].tolist()  # Assuming 'Phone' is the column name with the phone numbers

db= mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql",
    database="whatsapp"
)

cursor = db.cursor()
# Create a table to store user responses
cursor.execute("CREATE TABLE IF NOT EXISTS user_responses (phone_number TEXT, response TEXT, date_time DATETIME)")  

app = Flask(__name__)

# Function to send a WhatsApp message
def send_whatsapp_message(recipients, message_type, message_content, template_name=None, template_parameters=None):
    for to in recipients:
        url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
        headers = {'Content-Type': 'application/json','Authorization': f'Bearer {access_token}'}
        if message_type == 'text':
            data = {
                'recipient_type': 'individual',
                'to': to,
                'type': message_type,
                'text': {
                    'body': message_content
                },
                'messaging_product': 'whatsapp'
            }
        elif message_type == 'template':
            data = {
                'recipient_type': 'individual',
                'to': to,
                'type': message_type,
                'template': {
                    'name': template_name,
                    'language': {
                        'policy': 'deterministic',
                        'code': 'en_US'
                    },
                    'components': [
                        {
                            'type': 'body',
                            
                        }
                    ]
                },
                'messaging_product': 'whatsapp'
            }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print('Message sent:', response.json())
    return response

#call the function
response=send_whatsapp_message(recipients,"text" , "Hello from Mythought.ai!")
print(response.json())
template_parameters = ['Hello']
response=send_whatsapp_message(recipients,"template" , None, 'welcome_bot')
print(response.json())



def handle_message():
    body = request.get_json()
    # logging.info(f"request body: {body}")k
    print(body)
    # Check if it's a WhatsApp status update
    if (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    ):
        logging.info("Received a WhatsApp status update.")
        return jsonify({"status": "ok"}), 200

    try:
        #if is_valid_whatsapp_message(body):
            process_message(body)
            return jsonify({"status": "ok"}), 200
       
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON")
        return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400


def verify():
    # Parse params from the webhook verification request
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    expected_token = verify_token
    logging.info(f"Received token: {token}, expected token: {expected_token}")
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == expected_token:
            # Respond with 200 OK and challenge token from the request
            logging.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            logging.info("VERIFICATION_FAILED")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        logging.info("MISSING_PARAMETER")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400


@app.route('/webhook', methods=['GET'])
def webhook_get():
    return verify()

# Webhook to receive and process a WhatsApp message
@app.route('/webhook', methods=['POST'])
def webhook_post():
    return handle_message()

def process_message(body):
    message = request.json
    from_ =  body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    if message.get("type")== "text":
        message_body = message["text"]["body"]
        cursor.execute("INSERT INTO user_responses (phone_number, response, date_time) VALUES (%s, %s, %s)", (from_,message_body , datetime.now()))
        db.commit()
        #generate a response
        reply = generate_reply(message_body)
        send_whatsapp_message([from_], "text", reply)
    elif message.get("type")== "button":
        message_body= body["entry"][0]["changes"][0]["value"]["messages"][0]["button"]["text"]
        
        cursor.execute("INSERT INTO user_responses (phone_number, response, date_time) VALUES (%s, %s, %s)", (from_, message_body, datetime.now()))
        db.commit()
        reply = generate_reply(message_body)
        send_whatsapp_message([from_], "text", reply)
    

    return '', 200

def generate_reply(message):
    # This is a very basic example of how you can generate a reply.
    # You can replace this with your own logic.
    if "hello" in message.lower():
        return "Hello! How can I assist you today?"
    elif "help" in message.lower():
        return "Sure! What do you need help with?"
    else:
        return "I'm sorry, I don't understand. Please type 'help' for assistance."
 # Process the user message


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)