# 🎧 Mood Music App

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
