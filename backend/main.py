# ========== Imports ==========
import os
import cv2
import numpy as np
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from deepface import DeepFace

# ========== Load Environment Variables ==========
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ========== FastAPI Setup ==========
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== Models ==========
class MoodInput(BaseModel):
    mood_description: str

# ========== Helper Functions ==========
def analyze_emotion(img) -> dict:
    result = DeepFace.analyze(
        img,
        actions=['emotion'],
        detector_backend='retinaface',
        enforce_detection=False
    )
    data = result[0]
    dominant_emotion = data["dominant_emotion"].strip().lower()
    raw_emotions = data["emotion"]
    emotions = {k: float(v) for k, v in raw_emotions.items()}
    return {"dominant_emotion": dominant_emotion, "emotions": emotions}

# ========== Routes ==========
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        img_bytes = await file.read()
        img_array = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        emotion_data = analyze_emotion(img)
        return {
            "dominant_emotion": emotion_data["dominant_emotion"],
            "emotions": emotion_data["emotions"]
        }

    except Exception as e:
        print("Analyze error:", e)
        return {"error": str(e)}

@app.post("/ai-recommend")
async def ai_recommend(data: MoodInput):
    """
    Accepts mood_description, fetches user's saved Spotify songs,
    and asks Gemini which ones match the mood best.
    """

    # TEMP: Replace with your real token from https://developer.spotify.com/console/get-current-user-saved-tracks/
    access_token = "1POdFZRZbvb...qqillRxMr2z"

    try:
        # Step 1: Get user’s saved tracks
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            "https://api.spotify.com/v1/me/tracks?limit=10",
            headers=headers
        )

        if response.status_code != 200:
            return {"error": "Failed to fetch Spotify tracks", "details": response.text}

        data_json = response.json()
        items = data_json.get("items", [])
        if not items:
            return {"error": "No saved tracks found in user's library."}

        # Step 2: Format song list for Gemini
        song_lines = []
        for i, item in enumerate(items, start=1):
            track = item["track"]
            name = track["name"]
            artist = track["artists"][0]["name"]
            song_lines.append(f"{i}. {name} - {artist}")
        
        song_list_text = "\n".join(song_lines)
        mood = data.mood_description.strip()

        # Step 3: Send to Gemini
        gemini_prompt = (
            f"Based on the following mood: '{mood}', "
            f"select the top 3 songs from this list that emotionally fit best:\n\n"
            f"{song_list_text}\n\n"
            f"Only return the selected 3 songs as a list of 'Title - Artist'."
        )

        gemini_response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/text-bison-001:generateText?key={GOOGLE_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"prompt": {"text": gemini_prompt}, "temperature": 0.7}
        )

        if gemini_response.status_code != 200:
            return {"error": "Gemini API failed", "details": gemini_response.text}

        output = gemini_response.json().get("candidates", [{}])[0].get("output", "").strip()
        return {"suggested_songs": output}

    except Exception as e:
        return {"error": str(e)}
