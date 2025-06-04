from sqlalchemy import text
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from database_sqlalchemy import engine
from models import Base, User, Data
from fastapi import FastAPI
from endpoints_user import router as endpoints_router
from auth import router as auth_router
from endpoints_data import router as data_router
from database_sqlalchemy import SessionLocal

if __name__ == "__main__":  # nur wenn direkt ausgeführt
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Datenbank und Tabellen wurden erstellt.")

    db = SessionLocal()
    try:
        result = db.execute(text("PRAGMA table_info(data);"))
        print("Spalten in Tabelle 'data':")
        for row in result:
            print(f"- {row[1]} ({row[2]})")  # row[1] = Spaltenname, row[2] = Typ
    finally:
        db.close()


app = FastAPI()

 # Das habe ich geschrieben,damit frontend immer die Bilder holen kann.
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(endpoints_router)
app.include_router(auth_router)
app.include_router(data_router)




