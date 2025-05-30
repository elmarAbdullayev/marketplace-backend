from starlette.middleware.cors import CORSMiddleware
from database_sqlalchemy import engine
from models import Base
from fastapi import FastAPI
from endpoints import router as endpoints_router
from auth import router as auth_router

if __name__ == "__main__": # Dies Code wird nur ausgeführt, wenn du direkt python main.py startest
    # Die Tabellen werden erzeugt.
    Base.metadata.create_all(bind=engine)
    print("Datenbank und Tabellen wurden erstellt.")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(endpoints_router)
app.include_router(auth_router)




