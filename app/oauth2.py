from jose import JWTError, jwt
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from .config import settings
from .schema import TokenData
from fastapi import Depends, HTTPException, status
from .database import get_db
from sqlalchemy.orm import Session
from . import models

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode  = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        user_type: str = payload.get("user_type")

        if id is None or user_type is None:
            raise credentials_exception
        token_data = TokenData(id=id, user_type=user_type)
    except JWTError:
        raise credentials_exception
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )

    token_data = verify_access_token(token, credentials_exception)

    if token_data.user_type == "employer":
        user = db.query(models.Employer).filter(models.Employer.id == token_data.id).first()
    elif token_data.user_type == "candidate":
        user = db.query(models.Candidate).filter(models.Candidate.id == token_data.id).first()
    else:
        raise credentials_exception
    
    if user is None:
        raise credentials_exception 
    return user         
        





    
