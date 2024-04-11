from fastapi import APIRouter, Depends, Response, status, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from logging import getLogger
from typing import List, Union

from app.cruds import book as book_crud
from app.schemes import book as book_scheme
from app.schemes import res_msg as msg_scheme
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
async def books(user_id:int = Depends(jwt.get_current_user_id) ,db:AsyncSession = Depends(get_db)):
    return await book_crud.get_active_books(db, user_id)


@router.post("/",response_model=book_scheme.ResponseBook,status_code=201)
async def create_book(book_body: book_scheme.EnrollBook, db: AsyncSession = Depends(get_db), user_id:int = Depends(jwt.get_current_user_id)):
    dict_book_body = dict(book_body)
    dict_book_body.update({"user_id":user_id})
    entire_book_info = book_scheme.CreateBook(**dict_book_body)
    try:
        book = await book_crud.create_active_book(db,entire_book_info)
    except error.DuplicateError:
        raise HTTPException(status_code=400,detail="The book has been already enrolled.")
    return book


@router.get("/{book_id}",response_model=book_scheme.ResponseBook)
async def book(book_id:int,db:AsyncSession = Depends(get_db)):
    try:
        book = await book_crud.get_active_book(db,book_id)
    except error.NoObjectError:
        raise HTTPException(status_code=404)
    return book
# カスタムエラーはHTTPExceptionに統一するべき。後で取り組みたい。

@router.patch("/{book_id}",response_model=Union[book_scheme.ResponseBook,msg_scheme.Successful])
async def edit_book(book_id:int, book_body:book_scheme.ModifyBook,db:AsyncSession = Depends(get_db)):
    book = await book_crud.edit_active_book(db, book_body, book_id)
    if not book:
        return {"message":"No Alteration."}
    return book


@router.patch("/{book_id}/to_archive",status_code=204)
async def edit_book(book_id:int, response:Response, db: AsyncSession = Depends(get_db)):
    try:
        await book_crud.to_archive_book(db,book_id)
    except error.NoObjectError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error":"There is no book you want."}
        
    return 


@router.delete("/{book_id}", status_code=204)
async def eliminate_book(book_id:int, db: AsyncSession = Depends(get_db)):
    await book_crud.delete_active_book(db,book_id)
    return


@router.get("/rest_ratio/more")
async def get_books_by_pages_more(book_ratio:float, user_id:int = Depends(jwt.get_current_user_id), db:AsyncSession = Depends(get_db)):
    return await book_crud.get_active_books_more_than_rest_ratio(db,book_ratio, user_id)


@router.get("/rest_ratio/less")
async def get_books_by_pages_less(book_ratio:float, user_id:int = Depends(jwt.get_current_user_id), db:AsyncSession = Depends(get_db)):
    return await book_crud.get_active_books_less_than_rest_ratio(db,book_ratio, user_id)
