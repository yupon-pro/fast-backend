from fastapi import APIRouter, Depends, Response, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from logging import getLogger
from typing import List, Union

from app.cruds import book as book_crud
from app.schemes import book as book_scheme
from app.db import get_db
from app.utils import jwt
from app.utils import error

logger = getLogger("uvicorn")

bearer_scheme = HTTPBearer()

router = APIRouter(
        prefix="/api/books",
        dependencies=[Depends(jwt.verify_token), Depends(bearer_scheme)],
        responses={401:{"description":"Not Authorized"}}
    )


@router.get("/",response_model=List[book_scheme.ResponseBook])
async def books(db:AsyncSession = Depends(get_db)):
    return await book_crud.get_active_books(db)


@router.post("/",response_model=Union[book_scheme.ResponseBook,object],status_code=201)
async def create_book(book_body: book_scheme.EnrollBook,response:Response, db: AsyncSession = Depends(get_db), user_id:int = Depends(jwt.get_current_user_id)):
    dict_book_body = dict(book_body)
    dict_book_body.update({"user_id":user_id})
    entire_book_info = book_scheme.CreateBook(**dict_book_body)
    try:
        book = await book_crud.create_active_book(db,entire_book_info)
    except error.DuplicateError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error":"Your book has been already enrolled."}
    return book


@router.get("/{book_id}",response_model=book_scheme.ResponseBook)
async def book(book_id:int, db:AsyncSession = Depends(get_db)):
    return await book_crud.get_active_book(db,book_id)


@router.patch("/{book_id}",response_model=Union[book_scheme.ResponseBook,object])
async def edit_book(book_id:int, book_body:book_scheme.ModifyBook,db:AsyncSession = Depends(get_db)):
    user = await book_crud.edit_active_book(db, book_body, book_id)
    if not user:
        return {"message":"No Alteration."}
    return user


@router.patch("/{book_id}/to_archive",status_code=204)
async def edit_book(book_id:int, db: AsyncSession = Depends(get_db)):
    await book_crud.to_archive_book(db,book_id)
    return {"message":"Your book has been successfully archived."}


@router.delete("/{book_id}",status_code=204)
async def eliminate_book(book_id:int, db: AsyncSession = Depends(get_db)):
    await book_crud.delete_active_book(db,book_id)
    return {"message":"Your book has been successfully eliminated."}


@router.get("/rest_ratio/more")
async def get_books_by_pages_more(book_ratio:float, db:AsyncSession = Depends(get_db)):
    return await book_crud.get_active_books_more_than_rest_ratio(db,book_ratio)


@router.get("/rest_ratio/less")
async def get_books_by_pages_less(book_ratio:float, db:AsyncSession = Depends(get_db)):
    return await book_crud.get_active_books_less_than_rest_ratio(db,book_ratio)
