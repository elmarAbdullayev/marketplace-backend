from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    ID = Column(Integer, primary_key=True, index=True) # bei SQLAlchemy automatisch aktiviert, wenn du primary_key=True bei einem Integer-Feld angibst.
    name = Column(String(20))
    surname = Column(String(20))
    email = Column(String(40), unique=True, index=True)
    password = Column(String(30))
    street = Column(String(30))
    street_number = Column(Integer)
    number = Column(String(20))
    role = Column(String(10))
    created_at = Column(DateTime)

# Tabelle: data
class Data(Base):
    __tablename__ = "data"

    ID = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.ID"))
    title = Column(String(20))
    info = Column(String(40))
    category = Column(String(30))
    picture = Column(String(30))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)