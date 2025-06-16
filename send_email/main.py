import base64
import json
from googleapiclient.discovery import build
from google.cloud import secretmanager
from google.oauth2 import service_account
from email.mime.text import MIMEText

SENDER = "dan.zhu@insparx.com"
TO = "dan.zhu@insparx.com"

def get_credentials():
    """Load credentials.json from Google Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = "projects/390323574745/secrets/cloud-funktion-secret/versions/latest"
    response = client.access_secret_version(request={"name": name})
    credentials_json = json.loads(response.payload.data.decode("UTF-8"))

    credentials = service_account.Credentials.from_service_account_info(
        credentials_json,
        scopes=['https://www.googleapis.com/auth/gmail.send']
    )
    delegated_credentials = credentials.with_subject(SENDER)
    return delegated_credentials

def main(request):
    """Cloud Function triggered by Eventarc or HTTP to send email."""
    try:
        creds = get_credentials()
        service = build('gmail', 'v1', credentials=creds)

        message = MIMEText('BigQuery export is ready!')
        message['to'] = TO
        message['from'] = SENDER
        message['subject'] = 'BigQuery Table Update'

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body = {'raw': raw}
        service.users().messages().send(userId='me', body=body).execute()

        return 'Email sent successfully!'
    except Exception as e:
        return f"Error: {e}", 500
