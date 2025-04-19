import React, { Component, ErrorInfo, ReactNode } from 'react';
import styled from '@emotion/styled';
import { ErrorDisplay } from './ErrorDisplay';

const ErrorBoundaryContainer = styled.div`
    padding: 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background-color: #f8f9fa;
`;

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Uncaught error:', error, errorInfo);
    }

    public render() {
        if (this.state.hasError) {
            return (
                <ErrorBoundaryContainer>
                    <h1>Something went wrong</h1>
                    <ErrorDisplay
                        error={{
                            code: 'APP_ERROR',
                            message: this.state.error?.message || 'An unexpected error occurred',
                            details: this.state.error?.stack
                        }}
                        onRetry={() => {
                            this.setState({ hasError: false, error: null });
                            window.location.reload();
                        }}
                    />
                </ErrorBoundaryContainer>
            );
        }

        return this.props.children;
    }
} 