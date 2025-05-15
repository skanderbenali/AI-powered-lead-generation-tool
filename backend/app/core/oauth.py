from typing import Dict, Any
import os
from pydantic import BaseSettings


class OAuthConfig(BaseSettings):
    # Google OAuth settings
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    
    # GitHub OAuth settings
    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET", "")
    GITHUB_REDIRECT_URI: str = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/auth/github/callback")
    
    # Frontend URLs
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    FRONTEND_REDIRECT_URL: str = os.getenv("FRONTEND_REDIRECT_URL", "http://localhost:3000/auth/callback")
    
    class Config:
        env_file = ".env"


oauth_config = OAuthConfig()


# OAuth provider configurations
google_config = {
    "client_id": oauth_config.GOOGLE_CLIENT_ID,
    "client_secret": oauth_config.GOOGLE_CLIENT_SECRET,
    "authorize_url": "https://accounts.google.com/o/oauth2/auth",
    "token_url": "https://oauth2.googleapis.com/token",
    "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
    "redirect_uri": oauth_config.GOOGLE_REDIRECT_URI,
    "scope": "openid email profile",
}

github_config = {
    "client_id": oauth_config.GITHUB_CLIENT_ID,
    "client_secret": oauth_config.GITHUB_CLIENT_SECRET,
    "authorize_url": "https://github.com/login/oauth/authorize",
    "token_url": "https://github.com/login/oauth/access_token",
    "userinfo_url": "https://api.github.com/user",
    "redirect_uri": oauth_config.GITHUB_REDIRECT_URI,
    "scope": "read:user user:email",
}
