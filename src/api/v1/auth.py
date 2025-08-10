from datetime import datetime, timedelta
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt

from src.core.security import get_password_hash, verify_password
from src.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# In a real app, a database session dependency would be injected here.
# from src.db.session import get_db

router = APIRouter()

# --- Pydantic Models ---

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserPublic(UserBase):
    id: uuid.UUID

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserLogin(BaseModel):
    username: EmailStr  # We'll use the email as the username
    password: str

# --- FAKE DATABASE ---
# This dictionary serves as a stand-in for a real user database.
# In a real application, this would be replaced with database queries.
# The key is the user's email, and the value is a dictionary of user data.
fake_users_db = {}


# --- Helper Functions ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default expiration time if none is provided
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- API Endpoints ---

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
async def register_user(user: UserCreate):
    """
    Handles new user registration.
    - Hashes the user's password.
    - Stores the new user in our fake database.
    """
    if user.email in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    hashed_password = get_password_hash(user.password)
    user_id = uuid.uuid4()

    # In a real implementation, you would write this record to your `users` table.
    fake_users_db[user.email] = {
        "id": user_id,
        "email": user.email,
        "hashed_password": hashed_password
    }

    return {"id": user_id, "email": user.email}


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: UserLogin):
    """
    Authenticates a user and returns a JWT access token upon success.
    """
    # In a real implementation, you would query the database for the user.
    user_in_db = fake_users_db.get(form_data.username)

    if not user_in_db or not verify_password(form_data.password, user_in_db["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create the JWT with an expiration time
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_in_db["email"]}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
