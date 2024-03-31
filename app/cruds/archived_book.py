from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy.engine.cursor import CursorResult
from typing import List

from app.schemes import book as book_scheme
from app.models import book as book_model

async def get_archived_books(db:AsyncSession) -> List[book_scheme.DataBaseBook]:
    statement = text("""
                        SELECT *
                        FROM archived_book
                        JOIN user
                        ON archived_book.user_id = user.id
                        WHERE to_archive = true;
                    """)

    result:CursorResult = await db.execute(statement)

    return [book_scheme.DataBaseBook(**dict(zip(result.keys(),book_info))) for book_info in result.all()]


async def get_archived_book(db:AsyncSession, archived_book_id:int) -> book_scheme.DataBaseBook:
    statement = text("""
                        SELECT *
                        FROM archived_book
                        JOIN user
                        ON archived_book.user_id = user.id
                        WHERE id = :id;
                    """)
    
    result:CursorResult = await db.execute(statement,{"id":archived_book_id})

    return book_scheme.DataBaseBook(**dict(zip(result.keys(),result.one())))


async def to_activate_book(db:AsyncSession, archived_book_id:int):
    result:CursorResult = await db.execute(text("SELECT * FROM archived_book WHERE id = :id"),{"id":archived_book_id})
    await db.execute(text("DELETE FROM archived_book WHERE id = :id;"),{"id":archived_book_id})
    await db.commit()

    archived_book = result.one()
    archived_book.to_archive = False
    
    book = book_model.Book(**archived_book.dict())

    db.add(book)
    await db.commit()
    await db.refresh(book)

    return