from datetime import timedelta, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database_sqlalchemy import SessionLocal
from models import User
from jose import jwt,JWTError


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # bcrypt heisst Hash-Algorithmus.


oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

Secret_key = "elmar123"
Algorithm = "HS256"
Access_Token_Expire_Minute = 120


def create_token(data:dict,expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=Access_Token_Expire_Minute) # timedelta wird benutzt,um für Python klar zu machen,ob das minute ist.
    to_encode.update({"exp":expire})
    to_encode.update({"role": data["role"]})
    encoded_jwt = jwt.encode(to_encode,Secret_key,algorithm = Algorithm)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, Secret_key, algorithms=[Algorithm])
        user_email = payload.get("sub")
        user_role = payload.get("role")
        exp = payload.get("exp")

        if user_email is None or user_role is None:
            raise HTTPException(status_code=401, detail="Ungültiges Token")

        now_seconds = datetime.now().timestamp()

        if exp is None or now_seconds > int(exp):
            raise HTTPException(status_code=401, detail="Token ist abgelaufen")

        return {"email": user_email, "role": user_role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token-Fehler")



@router.post("/login")
def login(customer: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == customer.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Email oder Passwort ist falsch.")

    if not pwd_context.verify(customer.password, user.password):
        raise HTTPException(status_code=400, detail="Email oder Passwort ist falsch.")

    access_token_expires = timedelta(minutes=Access_Token_Expire_Minute)
    access_token = create_token(data={"sub": customer.username, "role": user.role}
                                ,expires_delta=access_token_expires)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.ID,
            "email": user.email,
            "role": user.role
        }
    }



