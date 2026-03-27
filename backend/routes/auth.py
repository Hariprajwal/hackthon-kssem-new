import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..database import get_db
from .. import models
from pydantic import BaseModel, EmailStr

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "HACKATHON_SECRET_KEY_CHANGE_THIS")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

router = APIRouter()

import random
import smtplib
from email.mime.text import MIMEText

OTP_STORE = {}

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    username: str
    password: str
    otp: str

class SendOTPRequest(BaseModel):
    email: EmailStr

class ForgotPasswordRequest(BaseModel):
    username: str
    new_password: str

class ResetPasswordRequest(BaseModel):
    current_password: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/send-otp")
async def send_otp(req: SendOTPRequest):
    otp = str(random.randint(100000, 999999))
    OTP_STORE[req.email] = otp
    print(f"\n[{datetime.utcnow().isoformat()}] 🚀 HACKATHON OTP GENERATED FOR {req.email}: {otp}\n")
    
    # Try sending real email if configured
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = (os.getenv("SMTP_PASS") or "").replace(" ", "")
    if smtp_user and smtp_pass:
        try:
            msg = MIMEText(f"Your CleanCodeX verification code is: {otp}")
            msg['Subject'] = "CleanCodeX Verification Code"
            msg['From'] = smtp_user
            msg['To'] = req.email
            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, req.email, msg.as_string())
        except Exception as e:
            print(f"SMTP Error: {e} (OTP was {otp})")
            
    return {"status": "success", "message": "OTP sent continuously to your email (check console if SMTP not configured)."}

@router.post("/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    if OTP_STORE.get(user.email) != user.otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")
    
    db_user = db.query(models.User).filter(
        (models.User.username == user.username) | (models.User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    new_user = models.User(
        name=user.name,
        email=user.email,
        username=user.username,
        password=get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Simple hackathon-level forgot password (no email verification)."""
    user = db.query(models.User).filter(models.User.username == req.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password = get_password_hash(req.new_password)
    db.commit()
    return {"status": "success", "message": "Password reset successfully"}

@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Reset password for an authenticated user."""
    if not verify_password(req.current_password, current_user.password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    current_user.password = get_password_hash(req.new_password)
    db.commit()
    return {"status": "success", "message": "Password updated successfully"}
