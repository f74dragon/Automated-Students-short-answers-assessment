from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models.user import User
from app.database.connection import get_db

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 token setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def get_password_hash(password: str):
    """Hash the password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    """Verify the password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Generate JWT token for authentication."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user by verifying hashed password."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Decode JWT token and return the authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    """Return the current authenticated user (if active)."""
    # Add additional checks here if needed, such as is_active flag
    return current_user

# Admin function removed as requested - all users have same privileges
