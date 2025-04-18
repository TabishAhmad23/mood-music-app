import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from urllib.parse import urlencode

app = FastAPI()

# Replace with your actual credentials
CLIENT_ID = "37b8207aa1c64599a567490f524e5f57"
CLIENT_SECRET = "53f41a4aa5a2485c9effc123c98258c4"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "user-library-read"

@app.get("/spotify-login")
def login():
    query_params = urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
    })

    auth_url = f"https://accounts.spotify.com/authorize?{query_params}"
    return RedirectResponse(auth_url)

@app.get("/callback", response_class=HTMLResponse)
def callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return HTMLResponse("<h2>❌ Authorization failed. No code returned.</h2>")

    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(token_url, data=payload, headers=headers)
    if response.status_code != 200:
        return HTMLResponse(f"<h2>❌ Token request failed</h2><p>{response.text}</p>")

    token_data = response.json()
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in")

    return HTMLResponse(f"""
        <h2>✅ Spotify Authorization Complete</h2>
        <p><strong>Access Token:</strong> {access_token}</p>
        <p><strong>Refresh Token:</strong> {refresh_token}</p>
        <p><strong>Expires in:</strong> {expires_in} seconds</p>
        <p>Copy your access token and paste it into your backend.</p>
    """)
