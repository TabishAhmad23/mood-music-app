import { useState, useCallback } from 'react';
import { ApiResponse, ApiError } from '../api/client';

interface UseApiRequestState<T> {
    data: T | null;
    loading: boolean;
    error: ApiError | null;
}

export function useApiRequest<T>() {
    const [state, setState] = useState<UseApiRequestState<T>>({
        data: null,
        loading: false,
        error: null
    });

    const execute = useCallback(async (promise: Promise<ApiResponse<T>>) => {
        setState(prev => ({ ...prev, loading: true, error: null }));
        try {
            const response = await promise;
            if (response.error) {
                setState(prev => ({ ...prev, loading: false, error: response.error || null }));
            } else {
                setState(prev => ({ ...prev, loading: false, data: response.data }));
            }
        } catch (error) {
            setState(prev => ({
                ...prev,
                loading: false,
                error: {
                    code: 'UNKNOWN_ERROR',
                    message: 'An unexpected error occurred'
                }
            }));
        }
    }, []);

    const reset = useCallback(() => {
        setState({ data: null, loading: false, error: null });
    }, []);

    return {
        ...state,
        execute,
        reset
    };
} 