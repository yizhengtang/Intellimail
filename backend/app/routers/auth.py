#auth.py
#FastAPI router for /auth/* endpoints.
#Handles connection status checks and sign-out for all three providers.
#Sign-out deletes the stored token file — the next API call will trigger a fresh OAuth login.

import os
from fastapi import APIRouter, HTTPException

from Gmail.gmail_api import initialize_gmail_service
from Outlook.outlook_api import initialize_outlook_service, make_graph_request as outlook_graph
from Teams.teams_api import initialize_teams_service, make_graph_request as teams_graph

router = APIRouter()

#Token file paths — these are the files that sign-out deletes.
#Gmail stores a JSON token file; Outlook and Teams each store a plain-text refresh token.
GMAIL_TOKEN_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'Gmail', 'token_files', 'token_gmail_v1.json'
)
OUTLOOK_TOKEN_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'Outlook', 'refresh_token.txt'
)
TEAMS_TOKEN_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'Teams', 'refresh_token.txt'
)


#Returns the connection status and logged-in email for all three providers.
#If the token file does not exist, the provider is immediately reported as not connected — no API call made.
#If the token file exists, a live /me call is made to retrieve the account email address.
#Falls back gracefully if the token is expired or invalid — reports not connected instead of raising.
@router.get("/status")
def auth_status():
    result = {
        "gmail":   {"connected": False, "email": None},
        "outlook": {"connected": False, "email": None},
        "teams":   {"connected": False, "email": None},
    }

    #Gmail — uses Google API client; getProfile returns emailAddress directly.
    if os.path.exists(GMAIL_TOKEN_PATH):
        try:
            service = initialize_gmail_service()
            profile = service.users().getProfile(userId='me').execute()
            result["gmail"] = {"connected": True, "email": profile.get("emailAddress")}
        except Exception:
            result["gmail"] = {"connected": False, "email": None}

    #Outlook — uses Microsoft Graph API; mail field holds the account email.
    #userPrincipalName is the fallback for accounts where mail is not populated.
    if os.path.exists(OUTLOOK_TOKEN_PATH):
        try:
            token = initialize_outlook_service()
            me = outlook_graph(token, 'me', params={'$select': 'mail,userPrincipalName'})
            email = me.get("mail") or me.get("userPrincipalName")
            result["outlook"] = {"connected": True, "email": email}
        except Exception:
            result["outlook"] = {"connected": False, "email": None}

    #Teams — same Microsoft Graph /me endpoint but uses the Teams-scoped token.
    #userPrincipalName is the fallback for accounts where mail is not populated.
    if os.path.exists(TEAMS_TOKEN_PATH):
        try:
            token = initialize_teams_service()
            me = teams_graph(token, 'me', params={'$select': 'mail,userPrincipalName'})
            email = me.get("mail") or me.get("userPrincipalName")
            result["teams"] = {"connected": True, "email": email}
        except Exception:
            result["teams"] = {"connected": False, "email": None}

    return result


#Deletes the stored token file for the given provider.
#The next API call to that provider will trigger a fresh OAuth browser login.
#If the token file does not exist, the endpoint still returns success — idempotent.
@router.post("/signout/{provider}")
def sign_out(provider: str):
    paths = {
        "gmail":   GMAIL_TOKEN_PATH,
        "outlook": OUTLOOK_TOKEN_PATH,
        "teams":   TEAMS_TOKEN_PATH,
    }

    if provider not in paths:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")

    token_path = paths[provider]
    if os.path.exists(token_path):
        os.remove(token_path)

    return {"status": "signed out", "provider": provider}


#Triggers the OAuth login flow for the given provider explicitly.
#This is the ONLY place in the backend that opens a browser for authentication.
#No other endpoint triggers OAuth — they return errors if the token file is missing.
@router.post("/connect/{provider}")
def connect(provider: str):
    try:
        if provider == "gmail":
            initialize_gmail_service()
        elif provider == "outlook":
            initialize_outlook_service()
        elif provider == "teams":
            initialize_teams_service()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        return {"status": "connected", "provider": provider}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
