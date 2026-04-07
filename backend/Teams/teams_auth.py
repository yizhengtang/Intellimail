#teams_auth.py
#MSAL OAuth2 authentication for Microsoft Teams via Microsoft Graph API.

import os
import webbrowser
import threading
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import msal
from dotenv import load_dotenv

load_dotenv()

MS_GRAPH_BASE_ENDPOINT = 'https://graph.microsoft.com/v1.0/'

#Teams stores its refresh token separately from Outlook.
#Outlook token has Mail.ReadWrite scope, whereas Teams token has Chat.ReadWrite scope.
REFRESH_TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'refresh_token.txt')

REDIRECT_URI = os.getenv('MICROSOFT_REDIRECT_URI')
REDIRECT_PORT = int(REDIRECT_URI.split(':')[-1].rstrip('/')) if REDIRECT_URI else 8090


#Temporary local HTTP server to capture the OAuth redirect callback automatically.
class _OAuthCallbackHandler(BaseHTTPRequestHandler):
    authorization_code = None

    def do_GET(self):
        #Parse the authorization code from the redirect URL query parameters
        query = parse_qs(urlparse(self.path).query)
        _OAuthCallbackHandler.authorization_code = query.get('code', [None])[0]

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<html><body><h3>Teams authentication successful. You can close this tab.</h3></body></html>')

        threading.Thread(target=self.server.shutdown).start()

    def log_message(self, format, *args):
        pass


#Starts a local server, opens the browser for consent, and captures the code automatically.
def _get_auth_code_via_local_server(auth_url):
    server = HTTPServer(('localhost', REDIRECT_PORT), _OAuthCallbackHandler)
    _OAuthCallbackHandler.authorization_code = None
    webbrowser.open(auth_url)
    server.serve_forever()
    return _OAuthCallbackHandler.authorization_code


#Acquires a Microsoft Graph access token using MSAL authorization code flow.
#On first run, opens a browser window and then user logs in with their school account.
#On subsequent runs, uses the stored refresh token silently.
def get_access_token(app_id, client_secret, scopes):
    client = msal.ConfidentialClientApplication(
        client_id=app_id,
        client_credential=client_secret,
        authority='https://login.microsoftonline.com/common'
    )

    refresh_token = None
    if os.path.exists(REFRESH_TOKEN_PATH):
        with open(REFRESH_TOKEN_PATH, 'r') as f:
            refresh_token = f.read().strip()

    if refresh_token:
        token_response = client.acquire_token_by_refresh_token(refresh_token, scopes=scopes)
    else:
        auth_url = client.get_authorization_request_url(scopes, redirect_uri=REDIRECT_URI)
        authorization_code = _get_auth_code_via_local_server(auth_url)

        if not authorization_code:
            raise ValueError("Authorization code is empty")

        token_response = client.acquire_token_by_authorization_code(
            code=authorization_code,
            scopes=scopes,
            redirect_uri=REDIRECT_URI
        )

    if 'access_token' in token_response:
        if 'refresh_token' in token_response:
            with open(REFRESH_TOKEN_PATH, 'w') as f:
                f.write(token_response['refresh_token'])
        return token_response['access_token']
    else:
        raise Exception("Failed to acquire Teams access token: " + str(token_response))
