from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import schema, models, oauth2
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=schema.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.Employer).filter(models.Employer.email == user_credentials.username).first()
    user_type = "employer"

    # If not employer then check if it's a candidate
    if not user:
        user = db.query(models.Candidate).filter(models.Candidate.email == user_credentials.username).first()
        user_type = "candidate"

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    flag = oauth2.verify_password(user_credentials.password, user.password)    
    if not flag:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    access_token = oauth2.create_access_token(data={"user_id" : user.id, "user_type" : user_type})
    return {"access_token": access_token, "token_type" : "bearer"}
