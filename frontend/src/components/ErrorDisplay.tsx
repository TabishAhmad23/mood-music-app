import React from 'react';
import styled from '@emotion/styled';
import { ApiError } from '../api/client';

const ErrorContainer = styled.div`
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 4px;
    background-color: #ffebee;
    color: #c62828;
`;

const ErrorTitle = styled.h3`
    margin: 0 0 0.5rem 0;
    font-size: 1.1rem;
`;

const ErrorMessage = styled.p`
    margin: 0;
    font-size: 0.9rem;
`;

const ErrorDetails = styled.pre`
    margin: 0.5rem 0 0 0;
    padding: 0.5rem;
    background-color: rgba(0, 0, 0, 0.05);
    border-radius: 4px;
    font-size: 0.8rem;
    white-space: pre-wrap;
`;

interface ErrorDisplayProps {
    error: ApiError;
    onRetry?: () => void;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, onRetry }) => {
    const getErrorMessage = (code: string) => {
        switch (code) {
            case 'HTTP_401':
                return 'Your session has expired. Please log in again.';
            case 'HTTP_429':
                return 'Too many requests. Please try again later.';
            case 'NETWORK_ERROR':
                return 'Network error. Please check your connection.';
            default:
                return error.message;
        }
    };

    return (
        <ErrorContainer>
            <ErrorTitle>Error: {error.code}</ErrorTitle>
            <ErrorMessage>{getErrorMessage(error.code)}</ErrorMessage>
            {error.details && (
                <ErrorDetails>{JSON.stringify(error.details, null, 2)}</ErrorDetails>
            )}
            {onRetry && (
                <button
                    onClick={onRetry}
                    style={{
                        marginTop: '1rem',
                        padding: '0.5rem 1rem',
                        backgroundColor: '#c62828',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    }}
                >
                    Retry
                </button>
            )}
        </ErrorContainer>
    );
}; 