from sqlalchemy import Column, Integer, String, Boolean, DateTime ,ForeignKey
from datetime import datetime

from app.db import Base

class ArchivedBook(Base):
    __tablename__ = "archived_book"

    id = Column(Integer, autoincrement=True ,primary_key=True)
    user_id = Column(Integer,ForeignKey("user.id"))
    whole_pages = Column(Integer,nullable=False)
    read_pages = Column(Integer)
    created_at = Column(DateTime, default=datetime.now())
    deadline = Column(DateTime)
    title = Column(String(1024),nullable=False)
    comment = Column(String(1024))
    to_archive = Column(Boolean, default=True)