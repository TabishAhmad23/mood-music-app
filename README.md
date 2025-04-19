# Mood Music App

A mood-based music recommendation application using Spotify integration.

## Prerequisites

- Python 3.8+
- Node.js 14+
- npm 6+
- Spotify Developer Account

## Environment Variables

### Backend (.env)
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:3000/callback
SECRET_KEY=your_secret_key
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000
```

## Installation

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
```

## Running the Application

### Backend
```bash
cd backend
uvicorn auth:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm start
```

## Production Deployment

1. Set up a production environment:
   - Use HTTPS
   - Set appropriate CORS origins
   - Configure proper session settings
   - Set up rate limiting

2. Update environment variables:
   - Use production Spotify credentials
   - Set secure secret keys
   - Configure production API URLs

3. Build frontend:
   ```bash
   cd frontend
   npm run build
   ```

4. Deploy backend:
   - Use a production-grade ASGI server (e.g., uvicorn with gunicorn)
   - Set up proper logging
   - Configure SSL/TLS

## Security Considerations

- All API endpoints are rate-limited
- Sessions are managed securely with HTTP-only cookies
- CORS is configured for specific origins
- Security headers are implemented
- Input validation is in place
- Token refresh is handled automatically

## API Documentation

Access the API documentation at:
- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`
- OpenAPI JSON: `/api/openapi.json`

## Health Check

The application provides a health check endpoint at `/health` that returns:
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": 1234567890
}
```

## Support

For issues and feature requests, please open an issue in the repository.

## 🎧 Mood Music App

An AI-powered web app that detects your mood from a photo and recommends a personalized Spotify playlist.

## 🔥 What It Does

- Upload a selfie or any facial image
- The app detects your **dominant emotion** using facial expression analysis
- It returns a **Spotify playlist** that matches your mood
- Built with modularity in mind — upcoming features include adaptive playlists, real-time webcam detection, and mood journaling

## ✨ Features

- 🎭 Emotion detection using **DeepFace**
- 📸 Image upload via a clean React UI (Material UI)
- 🎵 Playlist recommendation powered by the **Spotify API**
- ⚡ FastAPI backend with OpenCV and Spotipy integration

## 🧱 Tech Stack

| Layer      | Technology |
|------------|------------|
| Frontend   | React.js + Material UI |
| Backend    | FastAPI (Python) |
| AI Model   | DeepFace (pre-trained facial emotion recognition) |
| Music API  | Spotify + Spotipy |
| Image Processing | OpenCV |
| Deployment (soon) | Vercel + Render |

## 🚀 Getting Started (Local Setup)

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/mood-music-app.git
cd mood-music-app
