import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { ApiError } from '../api/client';

interface User {
    id: string;
    display_name: string;
    email: string;
}

interface AuthContextType {
    user: User | null;
    loading: boolean;
    error: ApiError | null;
    login: () => Promise<void>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<ApiError | null>(null);

    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        try {
            const response = await apiClient.getUserInfo();
            if (response.error) {
                setError(response.error);
                setUser(null);
            } else {
                setUser(response.data);
                setError(null);
            }
        } catch (err) {
            setUser(null);
            setError(err as ApiError);
        } finally {
            setLoading(false);
        }
    };

    const login = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await apiClient.loginWithSpotify();
            if (response.error) {
                setError(response.error);
            }
        } catch (err) {
            setError(err as ApiError);
        } finally {
            setLoading(false);
        }
    };

    const logout = async () => {
        try {
            setLoading(true);
            setError(null);
            // Add logout API call here when implemented
            setUser(null);
        } catch (err) {
            setError(err as ApiError);
        } finally {
            setLoading(false);
        }
    };

    const value = {
        user,
        loading,
        error,
        login,
        logout
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}; 