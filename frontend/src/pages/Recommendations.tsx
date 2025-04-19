import React from 'react';
import styled from '@emotion/styled';
import { useApiRequest } from '../hooks/useApiRequest';
import { apiClient } from '../api/client';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorDisplay } from '../components/ErrorDisplay';

const RecommendationsContainer = styled.div`
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
`;

const TrackList = styled.ul`
    list-style: none;
    padding: 0;
    margin: 0;
`;

const TrackItem = styled.li`
    padding: 1rem;
    margin-bottom: 1rem;
    border-radius: 4px;
    background-color: #f5f5f5;
    display: flex;
    align-items: center;
    justify-content: space-between;
`;

const TrackInfo = styled.div`
    flex: 1;
`;

const TrackName = styled.h3`
    margin: 0 0 0.5rem 0;
`;

const ArtistName = styled.p`
    margin: 0;
    color: #666;
`;

const Recommendations: React.FC = () => {
    const { data: tracks, loading, error, execute } = useApiRequest();

    React.useEffect(() => {
        execute(apiClient.getSavedTracks());
    }, [execute]);

    if (loading) {
        return <LoadingSpinner fullScreen />;
    }

    if (error) {
        return <ErrorDisplay error={error} onRetry={() => execute(apiClient.getSavedTracks())} />;
    }

    return (
        <RecommendationsContainer>
            <h1>Your Saved Tracks</h1>
            <TrackList>
                {tracks?.map((track) => (
                    <TrackItem key={track.external_urls.spotify}>
                        <TrackInfo>
                            <TrackName>{track.name}</TrackName>
                            <ArtistName>
                                {track.artists.map(artist => artist.name).join(', ')}
                            </ArtistName>
                        </TrackInfo>
                        <a
                            href={track.external_urls.spotify}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                                padding: '0.5rem 1rem',
                                backgroundColor: '#1DB954',
                                color: 'white',
                                textDecoration: 'none',
                                borderRadius: '4px'
                            }}
                        >
                            Play on Spotify
                        </a>
                    </TrackItem>
                ))}
            </TrackList>
        </RecommendationsContainer>
    );
};

export default Recommendations; 