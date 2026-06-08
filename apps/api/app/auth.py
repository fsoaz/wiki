from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_session
from .models import AuthUser
from .repository import get_user_by_token


def get_current_user(
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_session),
) -> AuthUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    token = authorization.removeprefix("Bearer ").strip()
    user = get_user_by_token(session, token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    return user


def require_contributor(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if user.role not in {"contributor", "reviewer", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Contributor access required")
    return user


def require_reviewer(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if user.role not in {"reviewer", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Reviewer access required")
    return user


def require_admin(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
