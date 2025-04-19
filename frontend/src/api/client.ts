import axios, { AxiosInstance, AxiosError } from 'axios';

export interface ApiError {
    code: string;
    message: string;
    details?: any;
}

export interface ApiResponse<T> {
    data?: T;
    error?: ApiError;
}

export interface Track {
    name: string;
    artists: Array<{ name: string }>;
    external_urls: { spotify: string };
}

export interface User {
    id: string;
    display_name: string;
    email: string;
}

interface ErrorResponse {
    message?: string;
    details?: any;
}

class ApiClient {
    private client: AxiosInstance;
    private retryCount = 0;
    private maxRetries = 2;

    constructor() {
        this.client = axios.create({
            baseURL: '/api',
            withCredentials: true,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        this.client.interceptors.response.use(
            (response) => response,
            async (error: AxiosError) => {
                if (this.shouldRetry(error) && this.retryCount < this.maxRetries) {
                    this.retryCount++;
                    const delay = Math.pow(2, this.retryCount) * 1000;
                    await new Promise(resolve => setTimeout(resolve, delay));
                    return this.client.request(error.config!);
                }
                this.retryCount = 0;
                return Promise.reject(this.handleError(error));
            }
        );
    }

    private shouldRetry(error: AxiosError): boolean {
        return (
            error.response?.status === 429 || // Rate limit
            error.response?.status === 503 || // Service unavailable
            error.code === 'ECONNABORTED' || // Timeout
            error.code === 'ECONNRESET'      // Connection reset
        );
    }

    private handleError(error: AxiosError): ApiError {
        if (error.response) {
            const errorData = error.response.data as ErrorResponse;
            return {
                code: `HTTP_${error.response.status}`,
                message: errorData?.message || 'An error occurred',
                details: errorData?.details
            };
        }
        return {
            code: 'NETWORK_ERROR',
            message: error.message || 'Network error occurred'
        };
    }

    async loginWithSpotify(): Promise<ApiResponse<void>> {
        try {
            const response = await this.client.get('/auth/spotify-login');
            return { data: undefined };
        } catch (error) {
            return { error: error as ApiError };
        }
    }

    async getSavedTracks(): Promise<ApiResponse<Track[]>> {
        try {
            const response = await this.client.get('/saved-tracks');
            return { data: response.data.tracks };
        } catch (error) {
            return { error: error as ApiError };
        }
    }

    async getUserInfo(): Promise<ApiResponse<User>> {
        try {
            const response = await this.client.get('/auth/me');
            return { data: response.data };
        } catch (error) {
            return { error: error as ApiError };
        }
    }
}

export const apiClient = new ApiClient(); 