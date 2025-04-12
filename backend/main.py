import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

SPOTIFY_CLIENT_ID = "37b8207aa1c64599a567490f524e5f57"
SPOTIFY_CLIENT_SECRET = "53f41a4aa5a2485c9effc123c98258c4"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# Map each emotion to Spotify genres
mood_to_genres = {
    "happy": ["pop", "dance"],
    "sad": ["acoustic", "piano"],
    "angry": ["metal", "hard-rock"],
    "fear": ["ambient", "soundtrack"],
    "disgust": ["experimental", "industrial"],
    "surprise": ["electronic", "funk"],
    "neutral": ["chill", "lofi"]
}

def get_playlist_for_emotion(emotion):
    genres = mood_to_genres.get(emotion, ["chill"])
    query = f"{genres[0]} playlist"
    
    results = sp.search(q=query, type="playlist", limit=1)
    playlists = results.get("playlists", {}).get("items", [])

    if playlists:
        return playlists[0]["external_urls"]["spotify"]
    
    return None




from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
from deepface import DeepFace

app = FastAPI()

# Enable CORS so frontend can access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        img_bytes = await file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        result = DeepFace.analyze(
            img,
            actions=['emotion'],
            detector_backend='retinaface',
            enforce_detection=False
        )

        dominant_emotion = result[0]["dominant_emotion"]
        raw_emotions = result[0]["emotion"]

        emotions = {k: float(v) for k, v in raw_emotions.items()}
        playlist_url = get_playlist_for_emotion(dominant_emotion)

        return {
            "dominant_emotion": dominant_emotion,
            "emotions": emotions,
            "playlist": playlist_url
        }

    except Exception as e:
        return {"error": str(e)}

