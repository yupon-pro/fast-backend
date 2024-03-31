from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

url = URL.create(
    drivername="mysql+aiomysql",
    username="yupon",
    password="yupon-db-2024",
    host="db",
    database="fast",
    query={"charset":"utf8"}
)

# hostの名前は、docker-compose.ymlファイルで定めた通りの、アプリ名。注意されたし。

ASYNC_ENGINE = create_async_engine(
    url,
    echo=True
)

ASYNC_SESSION = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=ASYNC_ENGINE,
            class_=AsyncSession
        )

Base = declarative_base()

async def get_db():
    async with ASYNC_SESSION() as session:
        yield session