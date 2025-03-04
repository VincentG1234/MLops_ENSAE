# user_auth.py

from firebase_admin import credentials, auth
import firebase_admin
from fastapi import Request

# Initialize Firebase
def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate("config/firebase_config.json")
        firebase_admin.initialize_app(cred)

# Function to handle login
def login_user(email, password):
    try:
        user = auth.get_user_by_email(email)
        # Note: Firebase Admin SDK does not support password verification.
        # In production, use Firebase Authentication REST API or client SDK.
        return user.email
    except Exception as e:
        return None

# Function to handle registration
def register_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        return user.email
    except Exception as e:
        return None

# Function to check if user is authenticated
def is_authenticated(request: Request):
    return 'user' in request.session
