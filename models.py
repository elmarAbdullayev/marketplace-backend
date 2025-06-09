from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    ID = Column(Integer, primary_key=True, index=True) # bei SQLAlchemy automatisch aktiviert, wenn du primary_key=True bei einem Integer-Feld angibst.
    name = Column(String(40))
    surname = Column(String(20))
    email = Column(String(60), unique=True, index=True)
    password = Column(String(100))
    street = Column(String(50))
    street_number = Column(Integer)
    number = Column(String(20))
    role = Column(String(20))
    created_at = Column(DateTime)

# Tabelle: data
class Data(Base):
    __tablename__ = "data"

    ID = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.ID"))
    title = Column(String(50))
    city = Column(String(20))
    info = Column(String(250))
    category = Column(String(30))
    picture = Column(String(255))
    picture_id = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)