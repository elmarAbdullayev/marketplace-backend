from fastapi import HTTPException
from fastapi import FastAPI, APIRouter, Depends
from sqlalchemy.orm import Session
from crud_user import get_alle_user,create_user,get_user_byid,delete_user,update_user
from pydantic import BaseModel, EmailStr
from database_sqlalchemy import SessionLocal
from auth import oauth2_schema,verify_token
from models import User


class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str
    street: str = None
    street_number: int = None
    phone_number: str = None
    role: str =None

router = APIRouter()

def get_db():
    db = SessionLocal() # das ist meine Verbindung mit der Datenbank.
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def create_new_user(user: UserCreate, db: Session =Depends(get_db)): # Depends(get_db) =  Bu fonksiyona başlamadan önce get_db() fonksiyonunu çalıştır ve sonucunu db olarak ver.”
    print(user.email,user.name,user.surname,user.password,user.street,user.street_number,user.phone_number,user.role)
    try:
        return create_user(db, user)
    except Exception as e:
        raise HTTPException(status_code = 400,detail=str(e))


@router.get("/test")
def test():
    print("test")



@router.get("/getuser")
def get_all_user(db: Session = Depends(get_db), token: str = Depends(oauth2_schema)):
    payload = verify_token(token)
    payload = db.query(User).filter(User.email == payload["email"]).first()
    if payload:
        if payload.role == "admin":
            return get_alle_user(db)
        else:
            raise HTTPException(status_code=403, detail="Nur Admins dürfen alle Benutzer sehen")
    else:
        raise HTTPException(status_code=403, detail="You don't have access.")


@router.get("/getuserbyid/{id}")
def get_user(id:int,db:Session=Depends(get_db),token:str=Depends(oauth2_schema)):
    payload = verify_token(token)
    if payload:
            try:
                return get_user_byid(db, id)
            except Exception as e:
                raise HTTPException(status_code=400,detail=str(e))
    else:
        raise HTTPException(status_code=403, detail="You don't have access.")

@router.post("/delete/{id}")
def user_remove(id:int,db:Session=Depends(get_db),token:str=Depends(oauth2_schema)):
    payload = verify_token(token)
    payload = db.query(User).filter(User.email == payload["email"]).first()
    if payload:
        if payload.role == "admin":
            try:
                delete_user(db,id)
                return {"detail": "User deleted successfully"}
            except Exception as e:
                raise HTTPException(status_code=400,detail=str(e))
        else:
            raise HTTPException(status_code=403, detail="Nur Admins dürfen alle Benutzer sehen")
    else:
        raise HTTPException(status_code=403, detail="You don't have access.")


@router.put("/put/{id}")
def put_user(id:int,data:dict,db:Session=Depends(get_db),token:str=Depends(oauth2_schema)):
    payload = verify_token(token)
    payload = db.query(User).filter(User.email == payload["email"]).first()
    if payload:
        try:
            update_user(db,id,data)
            return "Okey!!"
        except Exception as e:
            raise HTTPException(status_code=400,detail=str(e))
    else:
        raise HTTPException(status_code=403, detail="You don't have access.")











