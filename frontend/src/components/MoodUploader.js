/*import React, { useState } from 'react';
import axios from 'axios';
import { Button, Typography, Box, CircularProgress } from '@mui/material';

const MoodUploader = () => {
  const [image, setImage] = useState(null);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!image) return;
    const formData = new FormData();
    formData.append('file', image);

    setLoading(true);
    try {
      const res = await axios.post('http://127.0.0.1:8000/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResponse(res.data);
    } catch (err) {
      console.error(err);
      alert("Something went wrong.");
    }
    setLoading(false);
  };

  return (
    <Box textAlign="center" mt={4}>
      <input type="file" onChange={(e) => setImage(e.target.files[0])} />
      <Button variant="contained" onClick={handleUpload} sx={{ mt: 2 }}>
        Analyze Mood
      </Button>

      {loading && <CircularProgress sx={{ mt: 2 }} />}

      {response && (
        <Box mt={4}>
          <Typography variant="h5">Mood: {response.dominant_emotion}</Typography>
          <Typography variant="body1" sx={{ mt: 2 }}>
            Full Emotion Breakdown:
          </Typography>
          <pre>{JSON.stringify(response.emotions, null, 2)}</pre>
          <Button
            variant="outlined"
            sx={{ mt: 2 }}
            href={response.playlist}
            target="_blank"
          >
            Listen on Spotify
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default MoodUploader;*/


import React, { useState } from 'react';
import axios from 'axios';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Avatar,
  CircularProgress,
  Grid
} from '@mui/material';
import EmojiEmotionsIcon from '@mui/icons-material/EmojiEmotions';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const emojiMap = {
  happy: '😄',
  sad: '😢',
  angry: '😠',
  fear: '😨',
  disgust: '🤢',
  surprise: '😲',
  neutral: '😐'
};

const MoodUploader = () => {
  const [image, setImage] = useState(null);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!image) return;
    const formData = new FormData();
    formData.append('file', image);

    setLoading(true);
    try {
      const res = await axios.post('http://127.0.0.1:8000/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResponse(res.data);
    } catch (err) {
      console.error(err);
      alert("Something went wrong.");
    }
    setLoading(false);
  };

  const renderEmotionChart = () => {
    if (!response?.emotions) return null;

    const data = Object.entries(response.emotions).map(([key, value]) => ({
      emotion: key,
      value: parseFloat(value.toFixed(2))
    }));

    return (
      <Box mt={2}>
        <Typography variant="h6" gutterBottom>
          Emotion Breakdown
        </Typography>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={data} layout="vertical">
            <XAxis type="number" />
            <YAxis dataKey="emotion" type="category" />
            <Tooltip />
            <Bar dataKey="value" fill="#1DB954" />
          </BarChart>
        </ResponsiveContainer>
      </Box>
    );
  };

  return (
    <Box mt={4} textAlign="center">
      <input
        type="file"
        onChange={(e) => setImage(e.target.files[0])}
        style={{ marginBottom: '16px' }}
      />
      <Button variant="contained" onClick={handleUpload}>
        Analyze Mood
      </Button>

      {loading && <CircularProgress sx={{ mt: 4 }} />}

      {response && (
        <Card
          sx={{
            maxWidth: 600,
            mx: 'auto',
            mt: 4,
            p: 2,
            backgroundColor: '#191414',
            color: '#fff'
          }}
        >
          <CardContent>
            <Grid container alignItems="center" justifyContent="center" spacing={2}>
              <Grid item>
                <Avatar sx={{ bgcolor: '#1DB954' }}>
                  <EmojiEmotionsIcon />
                </Avatar>
              </Grid>
              <Grid item>
              <Typography variant="h5" sx={{ color: '#1DB954' }}>
                {emojiMap[response?.dominant_emotion] || '🎭'}{' '}
                {response?.dominant_emotion?.toUpperCase() || 'UNKNOWN'}
              </Typography>

              </Grid>
            </Grid>

            {renderEmotionChart()}

            {response.playlist && (
              <Box mt={3}>
                {response.playlist.image && (
                  <Box mb={1}>
                    <img
                      src={response.playlist.image}
                      alt="Playlist"
                      style={{
                        width: '100%',
                        maxHeight: '250px',
                        objectFit: 'cover',
                        borderRadius: '12px'
                      }}
                    />
                  </Box>
                )}
                <Typography variant="h6" sx={{ mt: 1 }}>
                  {response.playlist.name}
                </Typography>
                <Button
                  variant="contained"
                  href={response.playlist.url}
                  target="_blank"
                  sx={{ mt: 1, backgroundColor: '#1DB954', color: '#fff' }}
                >
                  Listen on Spotify
                </Button>
              </Box>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default MoodUploader;


