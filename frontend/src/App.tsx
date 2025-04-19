import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { PrivateRoute } from './routes/PrivateRoute';
import { LoadingSpinner } from './components/LoadingSpinner';
import { ErrorBoundary } from './components/ErrorBoundary';

// Lazy load components for better performance
const Login = React.lazy(() => import('./pages/Login'));
const Recommendations = React.lazy(() => import('./pages/Recommendations'));
const Settings = React.lazy(() => import('./pages/Settings'));
const Home = React.lazy(() => import('./pages/Home'));

const App: React.FC = () => {
    return (
        <ErrorBoundary>
            <Router>
                <AuthProvider>
                    <React.Suspense fallback={<LoadingSpinner fullScreen />}>
                        <Routes>
                            <Route path="/login" element={<Login />} />
                            <Route
                                path="/recommendations"
                                element={
                                    <PrivateRoute>
                                        <Recommendations />
                                    </PrivateRoute>
                                }
                            />
                            <Route
                                path="/settings"
                                element={
                                    <PrivateRoute>
                                        <Settings />
                                    </PrivateRoute>
                                }
                            />
                            <Route
                                path="/"
                                element={
                                    <PrivateRoute>
                                        <Home />
                                    </PrivateRoute>
                                }
                            />
                            <Route path="*" element={<Navigate to="/" replace />} />
                        </Routes>
                    </React.Suspense>
                </AuthProvider>
            </Router>
        </ErrorBoundary>
    );
};

export default App; 