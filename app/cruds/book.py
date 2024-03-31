from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy.engine.cursor import CursorResult
from typing import List, Optional
from logging import getLogger

from app.schemes import book as book_scheme
from app.schemes import user as user_scheme
from app.models import book as book_model
from app.models import archived_book as archived_book_model
from app.utils import error

logger = getLogger("uvicorn")

async def create_active_book(db: AsyncSession, book_create:book_scheme.CreateBook) -> book_scheme.ResponseBook:
    preparation = text("""
                            SELECT *
                            FROM book
                            WHERE :title in (SELECT DISTINCT title
                                            FROM book)
                            UNION
                            SELECT *
                            FROM archived_book
                            WHERE :title in (SELECT DISTINCT title
                                            FROM archived_book)
                            LIMIT 1;
                        """)
    
    result:CursorResult = await db.execute(preparation,{"title":book_create.title})

    if result.first() is not None:
        raise error.DuplicateError("The book has been already enrolled.")

    book = book_model.Book(**book_create.dict())
    # sqlalchemyのメソッドを用いて簡潔にデータベースとやり取りをしたいという時、
    # 必ず、どのテーブルと連絡するか明示するために、modelのインスタンス化を通して、データをやり取りしないといけない。

    db.add(book)
    await db.commit()
    await db.refresh(book)

    # addでセッション（python と mysqlとのやり取りの結びつき）にbookインスタンスが登録され、refreshにおいてデータベースでの変更がインスタンスに反映される。
    # もし、セッションを閉じたかったら、expireするだけでいい。

    result:CursorResult = await db.execute(text("SELECT email,username FROM user WHERE id = :id"),{"id":book.user_id})
    user_info = user_scheme.ConcatUserFromBook(**dict(zip(result.keys(),result.one())))

    book_info = dict(book_create)

    book_info.update({"id":book.id, "username":user_info.username,"email":user_info.email})

    return book_scheme.ResponseBook(**book_info)


async def get_active_books(db:AsyncSession) -> List[book_scheme.ResponseBook]:
    statement = text("""
                        SELECT book.*, user.username, user.email
                        FROM book
                        JOIN user
                        ON book.user_id = user.id
                        WHERE to_archive = false;
                    """)

    result:CursorResult = await db.execute(statement)

    return [book_scheme.ResponseBook(**dict(zip(result.keys(),book_info))) for book_info in result.all()]


async def get_active_books_more_than_rest_ratio(db:AsyncSession, rest_ration:float) -> List[book_scheme.ResponseBook]:
    statement = text("""
                        SELECT book.*, user.username, user.email
                        FROM book
                        JOIN user
                        ON book.user_id = user.id
                        WHERE read_page / total_page >= :ratio;
                    """)
    result:CursorResult = await db.execute(statement,{"ratio":rest_ration})

    return [book_scheme.ResponseBook(**dict(zip(result.keys(),book_info))) for book_info in result.all()]


async def get_active_books_less_than_rest_ratio(db:AsyncSession, rest_ration:float) -> List[book_scheme.ResponseBook]:
    statement = text("""
                        SELECT book.*, user.username, user.email
                        FROM book
                        JOIN user
                        ON book.user_id = user.id
                        WHERE read_page / total_page <= :ratio;
                    """)
    result:CursorResult = await db.execute(statement,{"ratio":rest_ration})
    books = result.all()
    logger.info()
    return [book_scheme.ResponseBook(**dict(zip(result.keys(),book_info))) for book_info in books]


async def get_active_book(db:AsyncSession, book_id:int) -> book_scheme.ResponseBook:
    statement = text("""
                        SELECT book.*, user.username, user.email
                        FROM book
                        JOIN user
                        ON book.user_id = user.id
                        WHERE book.id = :id;
                    """)
    
    result:CursorResult = await db.execute(statement,{"id":book_id})

    return book_scheme.ResponseBook(**dict(zip(result.keys(),result.one())))


async def edit_active_book(db:AsyncSession,book_edit:book_scheme.ModifyBook, book_id:int) -> book_scheme.ResponseBook:
    modification_list = [ f"{i} = '{j}'" for i,j in dict(book_edit).items() if j is not None]
    if len(modification_list) == 0:
        return False
    setter_sentence = modification_list[0] if len(modification_list) == 1 else ", ".join(modification_list)

    statement = text(f"""
                        UPDATE book
                        SET {setter_sentence}
                        WHERE id = :id;
                    """)
    
    await db.execute(statement,{"id":book_id})

    selector = text("""
                        SELECT book.*, user.username, user.email
                        FROM book 
                        JOIN user 
                        ON book.user_id = user.id 
                        WHERE book.id = :id
                    """)

    result:CursorResult = await db.execute(selector,{"id":book_id})

    await db.commit()

    return book_scheme.ResponseBook(**dict(zip(result.keys(),result.one())))


async def to_archive_book(db:AsyncSession, book_id:int):
    result = await db.execute(text("SELECT * FROM book WHERE id = :id;"),{"id":book_id})  
    await db.execute(text("DELETE FROM book WHERE id = :id;"),{"id":book_id})
    await db.commit()

    book = book_scheme.DataBaseBook(**dict(zip(result.keys(),result.one())))  
    book.to_archive = True
    
    archived_book = archived_book_model.ArchivedBook(**book.dict())
    db.add(archived_book)
    await db.commit()
    await db.refresh(archived_book)

    return


async def delete_active_book(db:AsyncSession, book_id:int):
    statement = text("""
                        DELETE FROM book
                        WHERE id = :id;
                    """)
    
    await db.execute(statement,{"id":book_id})
    await db.commit()

    return


