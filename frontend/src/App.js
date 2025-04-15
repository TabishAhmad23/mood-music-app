import React from 'react';
import MoodUploader from './components/MoodUploader';
import { Container, Typography } from '@mui/material';

function App() {
  return (
    <Container>
      <Typography variant="h3" textAlign="center" mt={4}>
        Mood Music Recommender
      </Typography>
      <MoodUploader />
    </Container>
  );
}

export default App;
