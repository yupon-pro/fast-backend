from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List, Optional

from app.cruds import archived_book as archived_book_crud
from app.schemes import book as book_scheme
from app.schemes import user as user_scheme
from app.utils.jwt import verify_token
from app.db import get_db
from app.utils import jwt

# !! 依存関係の注入は、パスに対する指定か、デコレーターに対する指定においてのみ有効 !!

router = APIRouter(
        prefix="/api/archive/books",
        dependencies=[Depends(verify_token)],
        responses={401:{"description":"Not Authorized"}}
    )

@router.get("/",response_model=List[book_scheme.ResponseBook])
async def books(db:AsyncSession = Depends(get_db)):
    return await archived_book_crud.get_archived_books(db)


@router.get("/{book_id}",response_model=book_scheme.ResponseBook)
async def book(book_id:int, db:AsyncSession = Depends(get_db)):
    return await archived_book_crud.get_archived_book(db,book_id)


@router.patch("/{book_id}/activate",response_model=book_scheme.ResponseBook)
async def edit_book(book_id:int, db:AsyncSession = Depends(get_db)):
    await archived_book_crud.to_activate_book(db, book_id)
    return {"message":"Your book has been successfully activated."}



