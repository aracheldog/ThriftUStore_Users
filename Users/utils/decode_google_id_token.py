from google.auth.transport import requests
from google.oauth2 import id_token

def verify_google_id_token(token, client_id):
    try:
        # Verify and decode the ID Token
        id_info = id_token.verify_oauth2_token(token, requests.Request(), client_id)
        # Extract user information
        user_id = id_info['sub']
        user_email = id_info['email']
        user_name = id_info['name']
        token_exp = id_info['exp']
        return {'user_id': user_id, 'user_email': user_email, 'name' : user_name, 'exp':token_exp, }
    except ValueError as e:
        # Handle invalid token
        print(f"Invalid token: {e}")
        return None

# Example usage
google_id_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjViMzcwNjk2MGUzZTYwMDI0YTI2NTVlNzhjZmE2M2Y4N2M5N2QzMDkiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiIyNTgyMzkyODQ3MTMtOG5iM2g3MmVibnAzOGIyYTFpMDkzdDZmZDJvZzE3N3AuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiIyNTgyMzkyODQ3MTMtOG5iM2g3MmVibnAzOGIyYTFpMDkzdDZmZDJvZzE3N3AuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTEyMDQ2OTA0NDM3MzIyNTc2MzIiLCJlbWFpbCI6InpvdXpoaWNoZW5nMDFAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImF0X2hhc2giOiJxUXRKZnVna24zWHRKWEh0anB4M0xnIiwibmFtZSI6IlpoaWNoZW5nIFpvdSIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NMcHNCTjNjaW1DUGNMYk9MbDhnY25fSktmQUFzQWx0S1BBQS1TMkc2Ulc9czk2LWMiLCJnaXZlbl9uYW1lIjoiWmhpY2hlbmciLCJmYW1pbHlfbmFtZSI6IlpvdSIsImxvY2FsZSI6ImVuLUdCIiwiaWF0IjoxNzAwMDcyODE3LCJleHAiOjE3MDAwNzY0MTd9.K3agHw436l13FjSJr3VTTf4y_54EGXNvTh1GWGVa609_KPoW6G6D7Jiubsfx-leDzFSgchYY_m09bHHpuZW2cBE1Z02Pl8KL41zw7vVAxs39OGijhaDe11hMhA2xovDVdTiJcRPlaXXKHD2dW16_tML1QrccD0Kg_fR0PYGkU9z-6prOjLgWg6iZbKRyrzG5bicrMCzWJ6v5A-ORY5ON_BXmSKXbN_VybE-YmXfOUoCOpSucVS0YTS_W2z3hP4mgwvBq5A4_MIqKn8Zw7b8jljNa2yuSOYmKGhlZZTyfrREROoWZLvAbhq4vOWDOBj_temhkpa_pommf03plq79cMQ'

google_client_id = '258239284713-8nb3h72ebnp38b2a1i093t6fd2og177p.apps.googleusercontent.com'  # Replace with your Google OAuth client ID

decoded_info = verify_google_id_token(google_id_token, google_client_id)
if decoded_info:
    print(decoded_info)