from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import timedelta
import requests
import json
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from jose import JWTError, jwt
from typing import Optional

from app.database import get_db
from app.schemas import User, UserCreate, Token, AuthProvider, OAuthUserInfo
from app.services.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM
)
from app.services.user import create_user, get_user_by_email, get_user_by_username
from app.services.oauth import authenticate_oauth_user, get_google_user_info, get_github_user_info
from app.core.oauth import google_config, github_config, oauth_config

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get the current user from the provided JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        
        if username is None or user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    # Get user from database
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
        
    return user


@router.get("/me", response_model=User)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get the current authenticated user's profile"""
    return current_user

# Initialize OAuth for Google and GitHub
# Create config with the environment variables
config = Config(environ={
    'GOOGLE_CLIENT_ID': google_config['client_id'],
    'GOOGLE_CLIENT_SECRET': google_config['client_secret'],
    'GITHUB_CLIENT_ID': github_config['client_id'],
    'GITHUB_CLIENT_SECRET': github_config['client_secret']
})
oauth = OAuth(config)

# Configure OAuth providers
oauth.register(
    name='google',
    client_id=google_config["client_id"],
    client_secret=google_config["client_secret"],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': google_config["scope"],
        'prompt': 'select_account',  # Force account selection every time
        'access_type': 'offline',  # Get refresh token
    }
)

oauth.register(
    name='github',
    client_id=github_config["client_id"],
    client_secret=github_config["client_secret"],
    authorize_url=github_config["authorize_url"],
    access_token_url=github_config["token_url"],
    client_kwargs={'scope': github_config["scope"]}
)


@router.post("/register", response_model=User)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user_by_email = get_user_by_email(db, email=user_data.email)
    if db_user_by_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    db_user_by_username = get_user_by_username(db, username=user_data.username)
    if db_user_by_username:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user_data_dict = user_data.dict()
    user_data_dict.pop("password")
    new_user = create_user(db, user_data_dict, hashed_password)
    
    return new_user


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "id": user.id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/google")
async def login_google(request: Request):
    """Redirect to Google OAuth authorization URL
    
    This implementation follows OAuth 2.0 best practices:
    1. Uses secure state parameter to prevent CSRF attacks
    2. Stores state in server-side session
    3. Uses a clean redirect URI for callback
    """
    try:
        # Verify credentials are set
        if not google_config['client_id'] or not google_config['client_secret']:
            raise ValueError("Google OAuth credentials are not properly configured")
        
        # Clear any existing OAuth session state to avoid conflicts
        if 'google_oauth_state' in request.session:
            del request.session['google_oauth_state']
            
        # Use full absolute URL for redirect to avoid path issues
        redirect_uri = google_config["redirect_uri"]
        
        # Log critical info for debugging (remove in production)
        print(f"[OAuth] Starting Google OAuth flow with redirect URI: {redirect_uri}")
            
        # Initiate OAuth flow with proper redirect URI
        # authorize_redirect automatically generates and stores the state parameter
        # in the session for CSRF protection
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception as e:
        print(f"[OAuth Error] Google login error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"OAuth initialization error: {str(e)}"},
        )


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback
    
    This implementation follows OAuth 2.0 best practices:
    1. Verifies the state parameter to prevent CSRF attacks
    2. Properly handles token exchange and ID token validation
    3. Implements comprehensive error handling
    4. Creates or authenticates user based on verified identity
    """
    try:
        # Log the callback for debugging (remove in production)
        print(f"[OAuth Callback] Received Google OAuth callback")
        
        # Check if CSRF state param is in the session
        if 'google_oauth_state' not in request.session:
            print(f"[OAuth Error] No OAuth state found in session")
            for key in request.session.keys():
                print(f"[Session Debug] Found key: {key}")
                
        # Exchange authorization code for tokens
        # This internally verifies the state parameter to prevent CSRF attacks
        token = await oauth.google.authorize_access_token(request)
        if not token:
            raise ValueError("Failed to obtain access token from Google")
        
        # Log the token structure for debugging
        print(f"[OAuth Token] Keys in token response: {token.keys()}")
        
        # Get user information directly from Google's userinfo endpoint
        # instead of relying on ID token parsing
        resp = await oauth.google.get('https://www.googleapis.com/oauth2/v3/userinfo', token=token)
        user_data = resp.json()
        
        # Log user data for debugging
        print(f"[OAuth UserInfo] Received user data: {user_data}")
        
        # Verify we got critical user information
        email = user_data.get("email")
        if not email:
            raise ValueError("Email not provided in Google OAuth response")
            
        print(f"[OAuth Success] Authenticated Google user: {email}")
        
        # Create standardized user info structure
        user_info = {
            "email": email,
            "name": user_data.get("name"),
            "picture": user_data.get("picture"),
            "auth_provider": "google",
            "sub": user_data.get("sub")  # Google's unique user ID
        }
        
        # Create or authenticate user in our system
        access_token, is_new_user = await authenticate_oauth_user(db, user_info)
        
        # Clean up the session after successful authentication
        if 'google_oauth_state' in request.session:
            del request.session['google_oauth_state']
        
        # Redirect to frontend with token
        redirect_url = f"{oauth_config.FRONTEND_REDIRECT_URL}?token={access_token['access_token']}&provider=google"
        if is_new_user:
            redirect_url += "&new_user=true"
            
        print(f"[OAuth Redirect] Redirecting to: {redirect_url}")
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        # Detailed error logging for debugging
        print(f"[OAuth Error] Google callback error: {str(e)}")
        
        # Include request info in error logs to help debugging
        print(f"[Request Debug] URL: {request.url}")
        print(f"[Request Debug] Query Params: {request.query_params}")
        
        # Return user-friendly error
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": f"Authentication failed: {str(e)}"},
        )


@router.get("/github")
async def login_github(request: Request):
    """Redirect to GitHub OAuth authorization URL"""
    try:
        # Log credentials for debugging (don't do this in production)
        print(f"GitHub OAuth credentials - Client ID: {github_config['client_id'][:5]}..., Secret: {github_config['client_secret'][:5] if github_config['client_secret'] else 'Not set'}...")
        
        # Verify credentials are set
        if not github_config['client_id'] or not github_config['client_secret']:
            raise ValueError("GitHub OAuth credentials are not properly configured")
            
        redirect_uri = github_config["redirect_uri"]
        print(f"GitHub OAuth redirect URI: {redirect_uri}")
        
        # Use request parameter for proper redirect handling
        return await oauth.github.authorize_redirect(request, redirect_uri)
    except Exception as e:
        print(f"GitHub OAuth error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"OAuth initialization error: {str(e)}"},
        )


@router.get("/github/callback")
async def github_callback(request: Request, db: Session = Depends(get_db)):
    """Handle GitHub OAuth callback"""
    try:
        token = await oauth.github.authorize_access_token(request)
        user_info = await get_github_user_info(token["access_token"])
        access_token, is_new_user = await authenticate_oauth_user(db, user_info)
        
        # Redirect to frontend with token
        redirect_url = f"{oauth_config.FRONTEND_REDIRECT_URL}?token={access_token['access_token']}&provider=github"
        if is_new_user:
            redirect_url += "&new_user=true"
        
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": f"Authentication failed: {str(e)}"},
        )
