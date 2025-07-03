from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "whatsapp_api1"

    uid = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    phone = Column(String(20))
    chat_id = Column(String(255))
