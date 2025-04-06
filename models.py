from sqlalchemy import Column, Integer, String, DateTime, func
from db import Base


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    path = Column(String, unique=True, nullable=False)
    url = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, unique=True, server_default=func.now())
