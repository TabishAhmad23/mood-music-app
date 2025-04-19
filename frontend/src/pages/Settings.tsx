import React from 'react';
import styled from '@emotion/styled';
import { useAuth } from '../contexts/AuthContext';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorDisplay } from '../components/ErrorDisplay';

const SettingsContainer = styled.div`
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
`;

const Section = styled.section`
    margin-bottom: 2rem;
    padding: 1rem;
    border-radius: 4px;
    background-color: #f5f5f5;
`;

const SectionTitle = styled.h2`
    margin: 0 0 1rem 0;
`;

const LogoutButton = styled.button`
    padding: 0.5rem 1rem;
    background-color: #dc3545;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;

    &:hover {
        background-color: #c82333;
    }
`;

const Settings: React.FC = () => {
    const { user, loading, error, logout } = useAuth();

    if (loading) {
        return <LoadingSpinner fullScreen />;
    }

    if (error) {
        return <ErrorDisplay error={error} />;
    }

    return (
        <SettingsContainer>
            <h1>Settings</h1>
            <Section>
                <SectionTitle>Account</SectionTitle>
                <p>Logged in as: {user?.display_name}</p>
                <LogoutButton onClick={logout}>Logout</LogoutButton>
            </Section>
            {/* Add more settings sections here */}
        </SettingsContainer>
    );
};

export default Settings; 