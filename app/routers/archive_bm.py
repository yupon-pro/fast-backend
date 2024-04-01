from fastapi import APIRouter, Depends, Response, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List, Union

from app.cruds import archived_book as archived_book_crud
from app.schemes import book as book_scheme
from app.schemes import res_msg as msg_scheme
from app.db import get_db
from app.utils import jwt
from app.utils import error

# !! 依存関係の注入は、パスに対する指定か、デコレーターに対する指定においてのみ有効 !!

bearer_scheme = HTTPBearer()

router = APIRouter(
        prefix="/api/archive/books",
        dependencies=[Depends(jwt.verify_token),Depends(bearer_scheme)],
        responses={401:{"description":"Not Authorized"}}
    )

@router.get("/",response_model=List[book_scheme.ResponseBook])
async def books(user_id:int = Depends(jwt.get_current_user_id), db:AsyncSession = Depends(get_db)):
    return await archived_book_crud.get_archived_books(db,user_id)


@router.get("/{book_id}",response_model=Union[book_scheme.ResponseBook, msg_scheme.Erroneous])
async def book(book_id:int,response:Response, user_id:int = Depends(jwt.get_current_user_id), db:AsyncSession = Depends(get_db)):
    try:
        archived_book = await archived_book_crud.get_archived_book(db,book_id,user_id)
    except error.NoObjectError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error":"There is no book you want."}
    return archived_book


@router.patch("/{book_id}/activate",response_model=Union[msg_scheme.Erroneous,msg_scheme.Successful])
async def edit_book(book_id:int, response:Response, user_id:int = Depends(jwt.get_current_user_id), db:AsyncSession = Depends(get_db)):
    try:
        await archived_book_crud.to_activate_book(db, book_id, user_id)
    except error.NoObjectError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error":"There is no book you want."}
    return {"message":"Your book has been successfully activated."}
