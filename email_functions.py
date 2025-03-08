import os
import json
import base64
import requests
import streamlit as st
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from groq import Groq

# Define Gmail API scope
#SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
SCOPES = ["https://mail.google.com/"]
CREDENTIALS_FILE = "client_secret_667390996187-kkb8lgruch34ka6u4mk1enu4o1jchp6b.apps.googleusercontent.com.json"
TOKEN_FILE = "new_token.json"

# Gmail Authentication
# def authenticate_gmail():
#     creds = None
#     if os.path.exists(TOKEN_FILE):
#         creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
#             creds = flow.run_local_server(port=0)
#         with open(TOKEN_FILE, "w") as token:
#             token.write(creds.to_json())
    
#     return creds

# from google.auth.exceptions import RefreshError

# def authenticate_gmail():
#     creds = None

#     # Check if token.json exists (previously authenticated)
#     if os.path.exists(TOKEN_FILE):
#         creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

#     # Refresh credentials if expired, else try to authenticate without browser
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             try:
#                 creds.refresh(Request())  # Refresh without browser
#             except RefreshError:
#                 raise RuntimeError(
#                     "🚨 Failed to refresh credentials. Delete 'token.json' and re-authenticate."
#                 )
#         else:
#             raise RuntimeError(
#                 "🚨 No valid credentials found. Authenticate locally once to generate 'token.json'."
#             )

    # return creds


# Define the scope for Gmail API access
#SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
SCOPES = ["https://mail.google.com/"]


# Set the paths for credentials and token file
CREDENTIALS_FILE = "client_secret_667390996187-kkb8lgruch34ka6u4mk1enu4o1jchp6b.apps.googleusercontent.com.json"
TOKEN_FILE = "new_token.json"
import os

CREDENTIALS_FILE = "C:/Users/Asus/.vscode/client_secret_667390996187-kkb8lgruch34ka6u4mk1enu4o1jchp6b.apps.googleusercontent.com.json"

if os.path.exists(CREDENTIALS_FILE):
    print("✅ Credentials file found!")
else:
    print("❌ Credentials file NOT found. Check the file location.")


def authenticate_gmail():
    creds = None

    # Authenticate if no valid token exists
    if os.path.exists("new_token.json"):
        creds = Credentials.from_authorized_user_file("new_token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)  # Opens browser for authentication

        # Save new token
        with open("new_token.json", "w") as token:
            token.write(creds.to_json())

    return creds

# Re-run authentication
authenticate_gmail()



# Fetch recent emails
def get_email(n=10):
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', maxResults=n, labelIds=['INBOX']).execute()
    messages = results.get('messages', [])

    email_list = []
    for msg in messages:
        msg_details = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_details['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown Sender")
        body = msg_details.get("snippet", "No Body")
        email_list.append({"from": sender, "subject": subject, "body": body})

    return email_list

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
if API_KEY is None:
    raise ValueError("🚨 ERROR: GROQ_API_KEY is not set. Check your .env file.")

# AI Email Manager function
def llama_call(user_input):
    """
    Takes a user prompt and applies it to manage recent emails using AI.
    """
    emails = get_email()
    email_texts = "\n\n".join([email["body"] for email in emails])

    system_instruction = (
        "You are an intelligent email manager. Your task is to help users handle their emails."
        "Only answer what user asks. If the use is asking general questions then make a general conversaion."
        "Talk about emails only if user requires."
        f"Emails in user inbox for context: {email_texts}"
    )

    client = Groq(api_key=API_KEY)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_input}
        ],
        model="llama-3.3-70b-versatile",
    )

    return chat_completion.choices[0].message.content
