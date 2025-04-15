import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
from deepface import DeepFace

# Spotify credentials
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

# Return Spotify playlist link for an emotion
"""def get_playlist_for_emotion(emotion):
    emotion = emotion.strip().lower()
    print("Detected emotion:", emotion)
    genres = mood_to_genres.get(emotion, ["chill"])
    print("Search query:", f"{genres[0]} playlist")


    try:
        results = sp.search(q=query, type="playlist", limit=1)
        playlists = results.get("playlists", {}).get("items", [])
        if playlists:
            playlist = playlists[0]
            return {
                "url": playlist["external_urls"]["spotify"],
                "name": playlist["name"],
                "image": playlist["images"][0]["url"] if playlist["images"] else None
            }
    except Exception as e:
        print("Spotify error:", e)

    return {
        "url": "https://open.spotify.com/playlist/37i9dQZF1DX4WYpdgoIcn6",
        "name": "Chill Hits",
        "image": None}"""

def get_playlist_for_emotion(emotion):
    emotion = emotion.strip().lower()
    genres = mood_to_genres.get(emotion, ["chill"])
    
    primary_query = f"{genres[0]} genre playlist"
    fallback_query = f"top {genres[0]} songs"

    def search_spotify(query):
        print(f"Spotify query: {query}")
        try:
            results = sp.search(q=query, type="playlist", limit=1)
            playlists = results.get("playlists", {}).get("items", [])
            print("Playlist search result:", playlists)

            for playlist in playlists:
                if playlist:
                    return {
                        "url": playlist["external_urls"]["spotify"],
                        "name": playlist["name"],
                        "image": playlist["images"][0]["url"] if playlist["images"] else None
                    }
        except Exception as e:
            print("Spotify search error:", e)
        return None

    result = search_spotify(primary_query)
    if result:
        return result

    result = search_spotify(fallback_query)
    if result:
        return result

    return {
        "url": "https://open.spotify.com/playlist/37i9dQZF1DX4WYpdgoIcn6",
        "name": "Chill Hits (Fallback)",
        "image": None
    }



# FastAPI app setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

        # ✅ Validate result
        if not result or not isinstance(result, list):
            return {"error": "No result from DeepFace"}
        
        data = result[0]
        if "dominant_emotion" not in data or "emotion" not in data:
            return {"error": "Incomplete emotion data from DeepFace"}

        dominant_emotion = data["dominant_emotion"].strip().lower()
        raw_emotions = data["emotion"]

        # Convert all values to native floats
        emotions = {k: float(v) for k, v in raw_emotions.items()}
        playlist_url = get_playlist_for_emotion(dominant_emotion)
        playlist_data = get_playlist_for_emotion(dominant_emotion)

        return {
        "dominant_emotion": dominant_emotion,
        "emotions": emotions,
        "playlist": playlist_data
}

    except Exception as e:
        print("Backend error:", e)
        return {"error": str(e)}
