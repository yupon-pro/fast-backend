from typing import Union, Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field

from app.schemes import user

class BaseBook(BaseModel):
    whole_pages: int = Field(ge=1)
    read_pages: Union[int,None] = Field(default=0)
    created_at: datetime = Field(default=datetime.now())
    deadline: Union[datetime,None] = Field(default=None, description="The date when you want to read the book by.")
    title: str = Field(..., example="JUSTICE -what the right thing to do?-")
    comment: Union[str, None] = None
    to_archive: bool = Field(default=False, description="If you finish reading the book, check the box. This book will move to archive database.")

class EnrollBook(BaseBook):
    pass

    class Config:
        orm_mode = True

class ModifyBook(BaseBook):
    whole_pages: Union[int, None] = Field(default=None,ge=1)
    read_pages: Union[int, None] = Field(default=None)
    created_at: Union[datetime, None] = Field(default=None)
    deadline: Union[datetime, None] = Field(default=None)
    title: Union[str, None] = Field(default=None)
    comment: Union[str, None] = Field(default=None)
    to_archive: Union[bool, None] = Field(default=None,example="false")

    class Config:
        orm_mode = True

class CreateBook(BaseBook):
    user_id: int = Field(ge=1)

    class Config:
        orm_mode = True

class DataBaseBook(CreateBook):
    id: int = Field(ge=1)

    class Config:
        orm_mode = True

class ResponseBook(DataBaseBook,user.ConcatUserFromBook):
    pass

    class Config:
        orm_mode = True
