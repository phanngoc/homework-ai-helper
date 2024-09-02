import json

def load_google_creds():
    with open('secret/client_secret_729346947261-6btkvj36hci72mtc5mpkp1pfmqo1pnob.apps.googleusercontent.com.json') as f:
        return json.load(f)['web']