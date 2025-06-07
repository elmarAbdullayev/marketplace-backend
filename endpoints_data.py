from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from models import Data
from database_sqlalchemy import SessionLocal
from auth import oauth2_schema, verify_token
from datetime import datetime
import cloudinary
import cloudinary.uploader
import os

router = APIRouter()



cloudinary.config(
    cloud_name="dxk1cscpy",
    api_key="526465149644698",
    api_secret="ZqlUxHOSM9jH2i-01XigMmuFTfY"
)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
@router.get("/getdata/")
def get_data(db: Session = Depends(get_db)):
    try:
        data_list = db.query(Data).all()
        return data_list
    except Exception as e:
        print(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve data")



@router.get("/getonedata/{id}")
def get_one_data(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_schema)):
    payload = verify_token(token)
    print("sss", payload)
    if payload is None:
        raise HTTPException(status_code=403, detail="Token is expired or invalid")
    return db.query(Data).filter(Data.ID == id).first()




@router.post("/savedata")
def savedata(
        user_id: int = Form(...),
        title: str = Form(...),
        info: str = Form(""),
        category: str = Form(...),
        city: str = Form(...),
        picture: UploadFile = File(...),
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_schema)
):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=403, detail="Token invalid or expired")

    # Validiere Dateityp
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    file_extension = os.path.splitext(picture.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")

    # Datei an Cloudinary senden
    try:
        picture.file.seek(0)  # File-Pointer sicherheitshalber zurücksetzen
        upload_result = cloudinary.uploader.upload(picture.file, folder="fastapi_uploads")
        image_url = upload_result.get("secure_url")
        if not image_url:
            raise Exception("Cloudinary did not return a secure URL")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")

    # In Datenbank speichern
    try:
        now = datetime.utcnow()
        new_data = Data(
            user_id=user_id,
            title=title,
            city=city,
            info=info,
            category=category,
            picture=image_url,
            created_at=now,
            updated_at=now,
        )
        db.add(new_data)
        db.commit()
        db.refresh(new_data)

        return {
            "status": "success",
            "message": "Advertisement created successfully",
            "image_url": image_url,
            "data": {
                "id": new_data.ID,
                "title": new_data.title,
                "city": new_data.city
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save to database: {str(e)}")
