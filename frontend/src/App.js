import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import './App.css';
import './components/ErrorBoundary.css';

function AppContent() {
  const [image, setImage] = useState(null);
  const [error, setError] = useState(null);
  const { user, loading, login, logout } = useAuth();

  const validateImage = (file) => {
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
    const maxSize = 5 * 1024 * 1024; // 5MB

    if (!validTypes.includes(file.type)) {
      throw new Error('Please upload a valid image file (JPEG, PNG)');
    }

    if (file.size > maxSize) {
      throw new Error('Image size should be less than 5MB');
    }

    return true;
  };

  const handleImageUpload = async (event) => {
    try {
      setError(null);
      const file = event.target.files[0];
      
      if (!file) {
        throw new Error('No file selected');
      }

      validateImage(file);
      
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to analyze image');
      }

      const data = await response.json();
      setImage(data);
    } catch (err) {
      setError(err.message);
      console.error('Error:', err);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Mood Music App</h1>
        {!user ? (
          <button onClick={login} className="login-button">
            Login with Spotify
          </button>
        ) : (
          <>
            <div className="user-info">
              <span>Welcome, {user.display_name}</span>
              <button onClick={logout} className="logout-button">
                Logout
              </button>
            </div>
            {error && <div className="error-message">{error}</div>}
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="file-input"
            />
            {image && (
              <div className="result">
                <h2>Detected Mood: {image.dominant_emotion}</h2>
                <div className="emotions">
                  {Object.entries(image.emotions).map(([emotion, value]) => (
                    <div key={emotion} className="emotion-bar">
                      <span>{emotion}:</span>
                      <div className="bar-container">
                        <div
                          className="bar"
                          style={{ width: `${value}%` }}
                        />
                      </div>
                      <span>{value.toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </header>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
