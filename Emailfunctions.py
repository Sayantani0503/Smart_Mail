import numpy as np
import pandas as pd
import os
import base64
import requests
import json
from dotenv import load_dotenv
import google.auth
import google.oauth2
import google_auth_oauthlib
import googleapiclient.discovery
from groq import Groq
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import webbrowser

print("All packages imported successfully!")



# Define the scope for Gmail API access
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Set the paths for credentials and token file
CREDENTIALS_FILE = "client_secret_667390996187-m59qndu1102mjqfvq586fpulnbn4vlam.apps.googleusercontent.com.json"
TOKEN_FILE = "token.json"
import os

CREDENTIALS_FILE = "C:/Users/Asus/.vscode/client_secret_667390996187-m59qndu1102mjqfvq586fpulnbn4vlam.apps.googleusercontent.com.json"

if os.path.exists(CREDENTIALS_FILE):
    print("✅ Credentials file found!")
else:
    print("❌ Credentials file NOT found. Check the file location.")


def authenticate_gmail():
    creds = None

    # Authenticate if no valid token exists
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)  # Opens browser for authentication

        # Save new token
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds

# Re-run authentication
authenticate_gmail()




SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def load_credentials():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return creds

# Function to retrieve the 3 most recent emails
def get_recent_emails(n=3):
    creds = load_credentials()
    service = build('gmail', 'v1', credentials=creds)
    
    # Fetch the most recent emails
    results = service.users().messages().list(userId='me', maxResults=n, labelIds=['INBOX']).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No new emails found.")
        return

    for i, msg in enumerate(messages, start=1):
        msg_details = service.users().messages().get(userId='me', id=msg['id']).execute()
        
        # Extract subject and sender
        headers = msg_details['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown Sender")

        print(f"📧 Email {i}")
        print(f"From: {sender}")
        print(f"Subject: {subject}\n")

        # Load environment variables from .env file
load_dotenv()

# Retrieve the API key
API_KEY = os.getenv("GROQ_API_KEY")

# Check if API key is loaded correctly
if API_KEY is None:
    raise ValueError("🚨 ERROR: GROQ_API_KEY is not set. Check your .env file.")

print("✅ API Key Loaded Successfully!")

def summarize_recent_emails():
    email_texts = get_recent_emails(n=3)
    
    # Check if emails were fetched successfully
    if not email_texts or "No new emails found." in email_texts:
        return "No recent emails to summarize."
    
    email_content = "\n\n".join(email_texts)  # Combine emails into one text block



    client = Groq(
        # This is the default and can be omitted
        api_key="g"+API_KEY,
    )

    chat_completion = client.chat.completions.create(
        messages = [
                {"role": "system", "content": "Summarize the following emails concisely and clearly:"},
                {"role": "user", "content": email_content}
            ],
        model="llama-3.3-70b-versatile",
    )

    return chat_completion.choices[0].message.content





