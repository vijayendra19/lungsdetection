from typing import Optional
from fastapi import Depends, HTTPException, Query, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.core.security import decode_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    header_token: Optional[str] = Depends(oauth2_scheme),
    query_token: Optional[str] = Query(None, alias="token"),
) -> User:
    """Decodes access token from header or query param and retrieves authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = header_token or query_token
    if not token:
        # Check Cookie or Authorization header fallback
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise credentials_exception
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verifies that the authenticated user account is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account",
        )
    return current_user
