import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr

from src.core.config import SECRET_KEY, ALGORITHM
# In a real application, you would have a function here to get a user from the database.
# For this MVP, we import the fake user database directly from the auth module.
from src.api.v1.auth import fake_users_db

# This defines the security scheme. The `tokenUrl` points to the login endpoint.
# FastAPI's docs will use this to show an "Authorize" button.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class TokenData(BaseModel):
    """Pydantic model for the data contained within the JWT."""
    email: str | None = None

class UserInDB(BaseModel):
    """Represents a user object as it is stored (e.g., in our fake DB)."""
    id: uuid.UUID
    email: EmailStr

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependency to get the current user from a JWT token.

    This function is used in protected endpoints. It does the following:
    1. Extracts the token from the Authorization header.
    2. Decodes the JWT to get the payload.
    3. Validates the payload to ensure it contains a user identifier (email).
    4. Fetches the user from the database (or our fake DB).
    5. Returns the user object (as a dict) if valid, otherwise raises an HTTP 401 exception.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    # In a real application, this would be a database query, e.g.:
    # user = crud.get_user_by_email(db, email=token_data.email)
    user = fake_users_db.get(token_data.email)

    if user is None:
        raise credentials_exception

    # The fake_users_db stores user data as a dict, which we return directly.
    return user
