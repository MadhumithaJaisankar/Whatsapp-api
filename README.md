# WhatsApp Message Processing Application

This application is a Flask-based server that interacts with the WhatsApp Business API to send messages and process incoming messages. It also stores the incoming messages in a MySQL database.

## Prerequisites

- Python 3.6 or higher
- Flask
- pandas
- mysql-connector-python
- requests
- oauth2client

You can install the necessary libraries using pip:

```bash
pip install flask pandas mysql-connector-python requests oauth2client
```
## Setup
1. Clone this repository to your local machine.
2. Install the necessary Python packages mentioned in the Prerequisites section.
3. You need to have a MySQL server running on your machine. Update the db variable in the main.py file with your MySQL server's details.
4. Update the access_token with your WhatsApp Business API access token, verify_token with your webhook verification token, recipients list variable phone numbers you want to send messages to in the main.py file.
   
## Running the Application
To run the application, navigate to the directory containing the main-mod.py file and run the following command:

```bash
python main.py
```
The server will start on 0.0.0.0:5000. You can interact with it using the /webhook endpoint.

## Launch ngrok
The steps below are taken from the ngrok documentation.

Once your app is running successfully on localhost, let's get it on the internet securely using ngrok!

1. Download the ngrok agent.
2. Go to the ngrok dashboard, click Your Authtoken, and copy your Authtoken.
3. Follow the instructions to authenticate your ngrok agent. You only have to do this once.
4. On the left menu, expand Cloud Edge and then click Domains.
5. On the Domains page, click + Create Domain or + New Domain. (here everyone can start with one free domain)
6. Start ngrok by running the following command in a terminal on your local desktop:
```
ngrok http 5000
```
7. ngrok will display a URL where your localhost application is exposed to the internet (copy this URL for use with Meta).

## Integrate WhatsApp
In the Meta App Dashboard, go to WhatsApp > Configuration, then click the Edit button.

- In the Edit webhook's callback URL popup, enter the URL provided by the ngrok agent to expose your application to the internet in the Callback URL field, with /webhook at the end (i.e. https://myexample.ngrok-free.app/webhook).
- Enter a verification token. This string is set up by you when you create your webhook endpoint. You can pick any string you like. Make sure to update this in your VERIFY_TOKEN environment variable.
- After you add a webhook to WhatsApp, WhatsApp will submit a validation post request to your application through ngrok. Confirm your localhost app receives the validation get request and logs WEBHOOK_VERIFIED in the terminal.
- Back to the Configuration page, click Manage.
- On the Webhook fields popup, click Subscribe to the messages field. Tip: You can subscribe to multiple fields.
- If your Flask app and ngrok are running, you can click on "Test" next to messages to test the subscription. You recieve a test message in upper case. If that is the case, your webhook is set up correctly.
