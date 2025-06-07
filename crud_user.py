from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from auth import pwd_context
from models import User
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str
    street: str = None
    street_number: int = None
    phone_number: str = None
    role: str = None


def get_alle_user(db:Session):
    if db:
        return db.query(User).all()
    else:
        raise HTTPException(status_code=400, detail="There is problem.")

def get_user_byid(db: Session, user_id: int):
        user =  db.query(User).filter(User.ID == user_id).first() # db.query(User) bedeutet:"Mache eine Datenbank-Abfrage, die alle Daten aus der Tabelle User abfragt."
        if user:
            return {
                "id": user.ID,
                "name": user.name,
                "surname": user.surname,
                "email": user.email,
                "number": user.number,
                "street": user.street,
                "street_number": user.street_number,
                "created_at": user.created_at,
            }
        else:
            raise HTTPException(status_code=400,detail=f"Es gibt kein user mit dieser ID nummber{user_id}")

def create_user(db: Session, user_data:UserCreate):

    myuser = db.query(User).filter(User.email == user_data.email).first()

    if(myuser):
        raise HTTPException(status_code=400, detail="The email exists already.")

    else:
        hashed_password = pwd_context.hash(user_data.password)

        new_user = User(
            name=user_data.name,
            surname=user_data.surname,
            email=user_data.email,
            password=hashed_password,
            street=user_data.street,
            street_number=user_data.street_number,
            number=user_data.phone_number,
            role=user_data.role,
            created_at=datetime.now()
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user


def delete_user(db:Session,user_id):
    user = db.query(User).filter(User.ID == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return print("Deleted")
    else:
        raise HTTPException(status_code=400,detail="User nicht gefunden.")


def update_user(db: Session, user_id: int, new_data: dict):
    user = db.query(User).filter(User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=400,detail="User nicht gefunden.")
    for key, value in new_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


