"""
Compatibility layer for handling version differences between packages
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union

# Re-export EmailStr from pydantic.
# This will ensure we're using a compatible version regardless of 
# pydantic or email-validator versions
try:
    from pydantic import EmailStr
except ImportError:
    from pydantic.types import EmailStr

# Ensure HTTPUrl is available
try:
    from pydantic import HttpUrl
except ImportError:
    from pydantic.types import HttpUrl
