from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import User

# Create router
router = APIRouter(prefix="/users", tags=["Users"])

# Note: We're not implementing the /me endpoint here anymore
# This will be handled by the /auth/me endpoint instead
