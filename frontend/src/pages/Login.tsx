import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorDisplay } from '../components/ErrorDisplay';
import styled from '@emotion/styled';

const LoginContainer = styled.div`
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 2rem;
`;

const LoginButton = styled.button`
    padding: 1rem 2rem;
    font-size: 1.1rem;
    background-color: #1DB954;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;

    &:hover {
        background-color: #1ed760;
    }

    &:disabled {
        background-color: #cccccc;
        cursor: not-allowed;
    }
`;

const Login: React.FC = () => {
    const { login, loading, error } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const from = (location.state as any)?.from?.pathname || '/';

    const handleLogin = async () => {
        await login();
        navigate(from, { replace: true });
    };

    return (
        <LoginContainer>
            <h1>Welcome to Mood Music</h1>
            <p>Connect with Spotify to get started</p>
            {error && <ErrorDisplay error={error} onRetry={handleLogin} />}
            <LoginButton onClick={handleLogin} disabled={loading}>
                {loading ? <LoadingSpinner /> : 'Login with Spotify'}
            </LoginButton>
        </LoginContainer>
    );
};

export default Login; 