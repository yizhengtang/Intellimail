#This script contains the function to generate user access token to connect to Microsoft Graph API using OAuth2 authentication.
import os
import webbrowser
import threading
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import msal

MS_GRAPH_BASE_ENDPOINT = 'https://graph.microsoft.com/v1.0/'

REFRESH_TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'refresh_token.txt')
REDIRECT_PORT = 8090
REDIRECT_URI = f'http://localhost:{REDIRECT_PORT}'


#Temporary local HTTP server to capture the OAuth redirect callback automatically.
class _OAuthCallbackHandler(BaseHTTPRequestHandler):
    authorization_code = None

    def do_GET(self):
        #Parse the authorization code from the redirect URL query parameters
        query = parse_qs(urlparse(self.path).query)
        _OAuthCallbackHandler.authorization_code = query.get('code', [None])[0]

        #Send a success page to the browser so the user knows it worked
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<html><body><h3>Authentication successful. You can close this tab.</h3></body></html>')

        #Shut down the server in a background thread to avoid blocking
        threading.Thread(target=self.server.shutdown).start()

    #Suppress the default request logging to keep the terminal clean
    def log_message(self, format, *args):
        pass


#This function starts a local server, opens the browser for consent, and captures the code automatically.
def _get_auth_code_via_local_server(auth_url):
    server = HTTPServer(('localhost', REDIRECT_PORT), _OAuthCallbackHandler)

    #Reset any previous code
    _OAuthCallbackHandler.authorization_code = None

    #Open the browser for user consent
    webbrowser.open(auth_url)

    #Block until the callback is received and the server shuts itself down
    server.serve_forever()

    return _OAuthCallbackHandler.authorization_code


#This function will handle the authentication process and return an access token for the Microsoft Graph API
def get_access_token(app_id, client_secret, scopes):
    #ConfidentialClientApplication is used here since it is a web app where client secrets can be securely stored in.
    client = msal.ConfidentialClientApplication(
        client_id = app_id,
        client_credential = client_secret,
        authority = 'https://login.microsoftonline.com/common'
    )

    #Check if there is a refresh token stored.
    refresh_token = None
    if os.path.exists(REFRESH_TOKEN_PATH):
        with open (REFRESH_TOKEN_PATH, 'r') as file:
            refresh_token = file.read().strip()

    if refresh_token:
        #If refresh token exists, try to acquire a new token using the refresh token
        token_response = client.acquire_token_by_refresh_token(refresh_token, scopes = scopes)
    else:
        #Perform authorization flow using a local server to capture the redirect automatically.
        #The redirect_uri must match what is configured in the Azure App Registration.
        auth_request_url = client.get_authorization_request_url(scopes, redirect_uri=REDIRECT_URI)
        authorization_code = _get_auth_code_via_local_server(auth_request_url)

        if not authorization_code:
            raise ValueError("Authorization code is empty")

        token_response = client.acquire_token_by_authorization_code(
            code = authorization_code,
            scopes = scopes,
            redirect_uri = REDIRECT_URI
        )

    if 'access_token' in token_response:
        if 'refresh_token' in token_response:
            with open(REFRESH_TOKEN_PATH, 'w') as file:
                file.write(token_response['refresh_token'])

        return token_response['access_token']
    else:
        raise Exception("Failed to acquire access token: " + str(token_response))
    
