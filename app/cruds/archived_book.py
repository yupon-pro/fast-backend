from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy.engine.cursor import CursorResult
from typing import List

from app.schemes import book as book_scheme
from app.models import book as book_model
from app.utils import error

async def get_archived_books(db:AsyncSession, user_id:int) -> List[book_scheme.ResponseBook]:
    statement = text("""
                        SELECT archived_book.*, email, username
                        FROM archived_book
                        JOIN user
                        ON archived_book.user_id = user.id
                        WHERE to_archive = true
                        AND archived_book.user_id = :user_id;
                    """)

    result:CursorResult = await db.execute(statement, {"user_id":user_id})

    return [book_scheme.ResponseBook(**dict(zip(result.keys(),book_info))) for book_info in result.all()]


async def get_archived_book(db:AsyncSession, archived_book_id:int, user_id:int) -> book_scheme.ResponseBook:
    statement = text("""
                        SELECT archived_book.*, email, username
                        FROM archived_book
                        JOIN user
                        ON archived_book.user_id = user.id
                        WHERE archived_book.id = :id
                        AND archived_book.user_id = :user_id;
                    """)
    
    result:CursorResult = await db.execute(statement,{"id":archived_book_id, "user_id":user_id})

    archived_book = result.first()
    if archived_book is None:
        raise error.NoObjectError("There is no book you want.")

    return book_scheme.ResponseBook(**dict(zip(result.keys(),archived_book)))


async def to_activate_book(db:AsyncSession, archived_book_id:int, user_id:int):
    result:CursorResult = await db.execute(text("""
                                                    SELECT * 
                                                    FROM archived_book 
                                                    WHERE id = :id 
                                                    AND archived_book.user_id = :user_id
                                                """),{
                                                "id":archived_book_id, 
                                                "user_id":user_id
                                            })
    
    tentative_archived_book = result.first()
    if tentative_archived_book is None:
        raise error.NoObjectError("There is no book you want.")
    
    archived_book = book_scheme.DataBaseBook(**dict(zip(result.keys(),tentative_archived_book)))      
    archived_book.to_archive = False

    await db.execute(text("DELETE FROM archived_book WHERE id = :id;"),{"id":archived_book_id})
    await db.commit()
    
    book = book_model.Book(**archived_book.dict())

    db.add(book)
    await db.commit()
    await db.refresh(book)

    return