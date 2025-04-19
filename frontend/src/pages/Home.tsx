import React from 'react';
import styled from '@emotion/styled';
import { useAuth } from '../contexts/AuthContext';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorDisplay } from '../components/ErrorDisplay';

const HomeContainer = styled.div`
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
`;

const WelcomeMessage = styled.h1`
    margin-bottom: 2rem;
`;

const Home: React.FC = () => {
    const { user, loading, error } = useAuth();

    if (loading) {
        return <LoadingSpinner fullScreen />;
    }

    if (error) {
        return <ErrorDisplay error={error} />;
    }

    return (
        <HomeContainer>
            <WelcomeMessage>
                Welcome, {user?.display_name || 'User'}!
            </WelcomeMessage>
            {/* Add more content here */}
        </HomeContainer>
    );
};

export default Home; 