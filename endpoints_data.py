from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from models import Data
from database_sqlalchemy import SessionLocal
from auth import oauth2_schema, verify_token
from datetime import datetime
from fastapi import Body

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
    if payload is None:
        raise HTTPException(status_code=403, detail="Token is expired or invalid")
    return db.query(Data).filter(Data.ID == id).first()


@router.get("/getusersdata/{id}")
def get_one_data(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_schema)):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=403, detail="Token is expired or invalid")
    return db.query(Data).filter(Data.user_id == id).all()



@router.delete("/deletedata/{id}")
def delete_data(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_schema)):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=403, detail="Token is expired or invalid")
    try:
        data = db.query(Data).filter(Data.ID == id).first()
        if data:
            if data.picture_id:
                print(data.picture_id)
                cloudinary.uploader.destroy(data.picture_id, invalidate=True)
            db.delete(data)
            db.commit()
            return {"status": "success", "message": "Advertisement deleted successfully"}
        else:
            return {"status": "error", "message": "Advertisement not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Problem deleting advertisement: {str(e)}")



@router.put("/putdata/{id}")
def put_data(
    id: int,
    data: dict = Body(...),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_schema)
):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=403, detail="Token is expired or invalid")
    try:

        key = data.get("title")
        value = data.get("value")
        item_id = data.get("itemId")
        print(f"Empfangener Schlüssel: {key}, Wert: {value}") # Verbessertes Logging
        my_data = db.query(Data).filter(Data.user_id == id, Data.ID == item_id).first()

        if not my_data:
            raise HTTPException(status_code=404, detail="Data not found")

        print(f"Prüfe, ob das Data-Objekt das Attribut '{key}' hat.") # Zusätzliches Logging
        if not hasattr(my_data, key):
            # Dies ist der wahrscheinlichste Punkt, der einen Fehler verursachen könnte.
            # Wenn der Schlüssel (z.B. "titel") nicht in Ihrem 'Data'-Modell existiert,
            # wird dieser Fehler ausgelöst.
            print(f"Data-Objekt hat Attribut '{key}' NICHT.") # Bestätigung des Fehlers
            raise HTTPException(status_code=400, detail="Ungültiges Feld")

        print(f"Setze Attribut '{key}' auf '{value}'.") # Zusätzliches Logging
        setattr(my_data ,key, value)
        db.commit()
        print("Commit erfolgreich!") # Bestätigung

        return {"status": "success", "message": "Advertisement updated successfully"}
    except Exception as e:
        # Dies fängt den 500er-Fehler ab und gibt die tatsächliche Fehlermeldung aus.
        # Dies ist entscheidend für die Fehlersuche!
        print(f"Eine Ausnahme ist aufgetreten: {e}")
        raise HTTPException(status_code=500, detail=f"Problem updating advertisement: {str(e)}")




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

    file_extension = os.path.splitext(picture.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")
    print(file_extension)

    try:
        picture.file.seek(0)
        upload_result = cloudinary.uploader.upload(picture.file, folder="fastapi_uploads")
        image_url = upload_result.get("secure_url")
        public_id = upload_result.get("public_id")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")

    try:
        now = datetime.utcnow()
        new_data = Data(
            user_id=user_id,
            title=title,
            city=city,
            info=info,
            category=category,
            picture=image_url,
            picture_id=public_id,
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

