import os
import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from models import Data
from database_sqlalchemy import SessionLocal
from auth import oauth2_schema, verify_token
from datetime import datetime

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/getdata/")
def get_data(db: Session = Depends(get_db)):
    return db.query(Data).all()


@router.get("/getonedata/{id}")
def get_one_data(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_schema)):
    payload = verify_token(token)
    print("sss", payload)
    if payload is None:
        raise HTTPException(status_code=403, detail="Token is expired or invalid")
    return db.query(Data).filter(Data.ID == id).first()




UPLOAD_DIRECTORY = Path("uploads").resolve()
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
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

    # Validiere Dateitype
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    file_extension = os.path.splitext(picture.filename)[1].lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")

    # Erstelle das Upload-Verzeichnis mit absoluten Pfad
    try:
        # Aktuelles Arbeitsverzeichnis ermitteln
        current_dir = os.getcwd()
        abs_upload_dir = os.path.join(current_dir, UPLOAD_DIRECTORY)

        # Verzeichnis erstellen falls es nicht existiert
        os.makedirs(abs_upload_dir, exist_ok=True)
        print(f"Upload directory created/verified at: {abs_upload_dir}")

    except Exception as e:
        print(f"Error creating upload directory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create upload directory: {str(e)}")

    # Generiere einzigartigen Dateinamen
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    filepath = os.path.join(abs_upload_dir, unique_filename)

    print(f"Saving file to: {filepath}")

    # Speichere die Datei
    try:
        # File pointer auf Anfang setzen
        picture.file.seek(0)

        # Datei speichern
        with open(filepath, "wb") as buffer:
            content = picture.file.read()
            buffer.write(content)

        print(f"File saved successfully: {filepath}")
        print(f"File size: {os.path.getsize(filepath)} bytes")

        # Überprüfen ob Datei existiert
        if not os.path.exists(filepath):
            raise Exception("File was not saved properly")

    except Exception as e:
        print(f"Error saving file: {str(e)}")
        # Aufräumen bei Fehlern
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print("Cleaned up failed file")
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")

    # URL für den Browser
    image_public_url = f"/uploads/{unique_filename}"

    # In Datenbank speichern
    try:
        now = datetime.utcnow()
        new_data = Data(
            user_id=user_id,
            title=title,
            city=city,
            info=info,
            category=category,
            picture=image_public_url,
            created_at=now,
            updated_at=now,
        )
        db.add(new_data)
        db.commit()
        db.refresh(new_data)

        print(f"Data saved to database with ID: {new_data.ID}")

        return {
            "status": "success",
            "message": "Advertisement created successfully",
            "image_url": image_public_url,
            "data": {
                "id": new_data.ID,
                "title": new_data.title,
                "city": new_data.city
            }
        }

    except Exception as e:
        print(f"Database error: {str(e)}")
        # Bei Datenbankfehler die Datei wieder löschen
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print("Cleaned up file due to database error")
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to save to database: {str(e)}")