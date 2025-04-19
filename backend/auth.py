import os
import time
import json
from typing import Optional, List, Dict, Any, Annotated
import httpx
from fastapi import FastAPI, Request, HTTPException, Depends, Response
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, BaseSettings, HttpUrl, validator, constr, Field
from dotenv import load_dotenv
import logging
import logging.handlers
from functools import lru_cache
import asyncio
from itsdangerous import URLSafeTimedSerializer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import secrets

# Configure structured logging
class StructuredLogFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
            
        return json.dumps(log_data)

# Set up logging configuration
def setup_logging():
    logger = logging.getLogger('auth')
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(StructuredLogFormatter())
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        'auth.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(StructuredLogFormatter())
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str
    SPOTIFY_REDIRECT_URI: HttpUrl
    SPOTIFY_SCOPES: str = "user-library-read"
    SPOTIFY_AUTH_URL: str = "https://accounts.spotify.com/authorize"
    SPOTIFY_TOKEN_URL: str = "https://accounts.spotify.com/api/token"
    SPOTIFY_API_URL: str = "https://api.spotify.com/v1"
    HTTP_TIMEOUT: int = 30
    HTTP_RETRIES: int = 3
    HTTP_BACKOFF_FACTOR: float = 0.5
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    CORS_METHODS: List[str] = ["GET", "POST", "OPTIONS"]
    CORS_HEADERS: List[str] = ["*"]
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    SESSION_COOKIE_NAME: str = "session"
    SESSION_MAX_AGE: int = 1800  # 30 minutes
    RATE_LIMIT: str = "5/minute"

    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'LOG_LEVEL must be one of {valid_levels}')
        return v.upper()

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

class TokenResponse(BaseModel):
    """Response model for Spotify OAuth token exchange"""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str

    class Config:
        schema_extra = {
            "example": {
                "access_token": "BQBP...",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "AQB...",
                "scope": "user-library-read"
            }
        }

class Track(BaseModel):
    """Spotify track model"""
    name: str
    artists: List[dict]
    external_urls: dict

    class Config:
        schema_extra = {
            "example": {
                "name": "Bohemian Rhapsody",
                "artists": [{"name": "Queen"}],
                "external_urls": {"spotify": "https://open.spotify.com/track/..."}
            }
        }

class SessionData(BaseModel):
    """User session data model"""
    user_id: str
    access_token: str
    refresh_token: str
    expires_at: int

    class Config:
        schema_extra = {
            "example": {
                "user_id": "123456789",
                "access_token": "BQBP...",
                "refresh_token": "AQB...",
                "expires_at": 1672531200
            }
        }

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

class AuthService:
    def __init__(self, settings: Settings = Depends(get_settings)):
        self.settings = settings
        self.client = httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT)
        self.serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        self.limiter = Limiter(key_func=get_remote_address)
        logger.info("AuthService initialized")

    def create_session(self, user_id: str, access_token: str, refresh_token: str) -> str:
        expires_at = int(time.time()) + self.settings.SESSION_MAX_AGE
        session_data = SessionData(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at
        )
        return self.serializer.dumps(session_data.dict())

    def get_session(self, session_token: str) -> Optional[SessionData]:
        try:
            data = self.serializer.loads(session_token, max_age=self.settings.SESSION_MAX_AGE)
            return SessionData(**data)
        except:
            return None

    async def get_authorization_url(self, state: Optional[str] = None) -> str:
        logger.info("Generating authorization URL", extra={"state": state})
        params = {
            "client_id": self.settings.SPOTIFY_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": str(self.settings.SPOTIFY_REDIRECT_URI),
            "scope": self.settings.SPOTIFY_SCOPES,
        }
        if state:
            params["state"] = state

        auth_url = f"{self.settings.SPOTIFY_AUTH_URL}?{httpx.URL(params=params).query}"
        logger.debug("Authorization URL generated", extra={"url": auth_url})
        return auth_url

    async def exchange_code_for_token(self, code: str) -> TokenResponse:
        logger.info("Exchanging code for token")
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": str(self.settings.SPOTIFY_REDIRECT_URI),
            "client_id": self.settings.SPOTIFY_CLIENT_ID,
            "client_secret": self.settings.SPOTIFY_CLIENT_SECRET,
        }

        for attempt in range(self.settings.HTTP_RETRIES):
            try:
                logger.debug(f"Token exchange attempt {attempt + 1}")
                response = await self.client.post(
                    self.settings.SPOTIFY_TOKEN_URL,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                token_data = response.json()
                logger.info("Token exchange successful")
                return TokenResponse(**token_data)
            except httpx.HTTPStatusError as e:
                logger.error("Token exchange failed", extra={
                    "status_code": e.response.status_code,
                    "response": e.response.text,
                    "attempt": attempt + 1
                })
                if e.response.status_code == 400:
                    raise HTTPException(status_code=400, detail="Invalid authorization code")
                if attempt == self.settings.HTTP_RETRIES - 1:
                    raise HTTPException(status_code=500, detail="Failed to exchange code for token")
                await self._backoff(attempt)
            except httpx.RequestError as e:
                logger.error("Network error during token exchange", extra={
                    "error": str(e),
                    "attempt": attempt + 1
                })
                if attempt == self.settings.HTTP_RETRIES - 1:
                    raise HTTPException(status_code=500, detail="Network error during token exchange")
                await self._backoff(attempt)

    async def _backoff(self, attempt: int):
        delay = self.settings.HTTP_BACKOFF_FACTOR * (2 ** attempt)
        logger.warning(f"Request failed, retrying in {delay} seconds...")
        await asyncio.sleep(delay)

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        logger.info("Refreshing access token")
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.settings.SPOTIFY_CLIENT_ID,
            "client_secret": self.settings.SPOTIFY_CLIENT_SECRET,
        }

        for attempt in range(self.settings.HTTP_RETRIES):
            try:
                logger.debug(f"Token refresh attempt {attempt + 1}")
                response = await self.client.post(
                    self.settings.SPOTIFY_TOKEN_URL,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                token_data = response.json()
                logger.info("Token refresh successful")
                return TokenResponse(**token_data)
            except httpx.HTTPStatusError as e:
                logger.error("Token refresh failed", extra={
                    "status_code": e.response.status_code,
                    "response": e.response.text,
                    "attempt": attempt + 1
                })
                if e.response.status_code == 400:
                    raise HTTPException(status_code=401, detail="Invalid refresh token")
                if attempt == self.settings.HTTP_RETRIES - 1:
                    raise HTTPException(status_code=500, detail="Failed to refresh token")
                await self._backoff(attempt)
            except httpx.RequestError as e:
                logger.error("Network error during token refresh", extra={
                    "error": str(e),
                    "attempt": attempt + 1
                })
                if attempt == self.settings.HTTP_RETRIES - 1:
                    raise HTTPException(status_code=500, detail="Network error during token refresh")
                await self._backoff(attempt)

    async def get_valid_token(self, session: SessionData) -> str:
        if time.time() > session.expires_at:
            logger.info("Access token expired, refreshing")
            new_tokens = await self.refresh_token(session.refresh_token)
            
            # Update session with new tokens
            session.access_token = new_tokens.access_token
            session.expires_at = int(time.time()) + new_tokens.expires_in
            
            # Update session cookie
            session_token = self.create_session(
                session.user_id,
                session.access_token,
                session.refresh_token
            )
            
            return session.access_token, session_token
        return session.access_token, None

app = FastAPI(
    title="Mood Music API",
    description="API for mood-based music recommendations using Spotify integration",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)
settings = get_settings()
auth_service = AuthService()

# Add middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie=settings.SESSION_COOKIE_NAME,
    max_age=settings.SESSION_MAX_AGE,
    same_site="lax",
    https_only=True
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Add rate limiting
app.state.limiter = auth_service.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get(
    "/spotify-login",
    summary="Initiate Spotify OAuth flow",
    description="Redirects to Spotify's authorization page to start the OAuth flow",
    responses={
        302: {"description": "Redirect to Spotify authorization page"},
        429: {"description": "Rate limit exceeded"}
    }
)
@auth_service.limiter.limit(settings.RATE_LIMIT)
async def spotify_login(request: Request):
    state = secrets.token_urlsafe(16)
    auth_url = await auth_service.get_authorization_url(state)
    response = RedirectResponse(url=auth_url)
    response.set_cookie(
        "state",
        state,
        max_age=300,  # 5 minutes
        httponly=True,
        secure=True,
        samesite="lax"
    )
    return response

@app.get(
    "/callback",
    summary="OAuth callback endpoint",
    description="Handles the OAuth callback from Spotify, exchanges code for tokens, and creates a session",
    responses={
        302: {"description": "Redirect to frontend with session cookie"},
        400: {"description": "Invalid state parameter or authorization code"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@auth_service.limiter.limit(settings.RATE_LIMIT)
async def callback(request: Request, code: str, state: Optional[str] = None):
    try:
        stored_state = request.cookies.get("state")
        if not stored_state or stored_state != state:
            raise HTTPException(status_code=400, detail="Invalid state parameter")

        tokens = await auth_service.exchange_code_for_token(code)
        
        # Get user info from Spotify
        user_info = await get_user_info(tokens.access_token)
        
        # Create session
        session_token = auth_service.create_session(
            user_info["id"],
            tokens.access_token,
            tokens.refresh_token
        )
        
        response = RedirectResponse(url="/")
        response.set_cookie(
            settings.SESSION_COOKIE_NAME,
            session_token,
            max_age=settings.SESSION_MAX_AGE,
            httponly=True,
            secure=True,
            samesite="lax"
        )
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Callback error", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))

async def get_user_info(access_token: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.SPOTIFY_API_URL}/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        return response.json()

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: int

class TrackQueryParams(BaseModel):
    limit: Annotated[int, Field(ge=1, le=50)] = 20
    offset: Annotated[int, Field(ge=0)] = 0

@app.get(
    "/health",
    summary="Health check endpoint",
    description="Returns the health status of the API",
    response_model=HealthResponse
)
async def health_check():
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=int(time.time())
    )

@app.get(
    "/saved-tracks",
    summary="Get user's saved tracks",
    description="Retrieves the user's saved tracks from Spotify",
    responses={
        200: {
            "description": "List of saved tracks",
            "content": {
                "application/json": {
                    "example": {
                        "tracks": [
                            {
                                "name": "Bohemian Rhapsody",
                                "artists": [{"name": "Queen"}],
                                "external_urls": {"spotify": "https://open.spotify.com/track/..."}
                            }
                        ]
                    }
                }
            }
        },
        401: {"description": "Not authenticated or invalid session"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@auth_service.limiter.limit(settings.RATE_LIMIT)
async def get_saved_tracks(
    request: Request,
    response: Response,
    query_params: TrackQueryParams = Depends()
):
    try:
        session_token = request.cookies.get(settings.SESSION_COOKIE_NAME)
        if not session_token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        session = auth_service.get_session(session_token)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid session")

        access_token, new_session_token = await auth_service.get_valid_token(session)
        
        if new_session_token:
            response.set_cookie(
                settings.SESSION_COOKIE_NAME,
                new_session_token,
                max_age=settings.SESSION_MAX_AGE,
                httponly=True,
                secure=True,
                samesite="lax"
            )

        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SPOTIFY_API_URL}/me/tracks",
                params={"limit": query_params.limit, "offset": query_params.offset},
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            return {"tracks": [Track(**item["track"]) for item in data["items"]]}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error fetching saved tracks", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3000) 