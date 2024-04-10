from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from app.models.user import Base as UserBase
from app.models.book import Base as BookBase
from app.models.archived_book import Base as ArchivedBookBase
from os import environ

url = URL.create(
    drivername="mysql+aiomysql",
    username=environ.get('MYSQL_USER'),
    password=environ.get('MYSQL_PASSWORD'),
    host="db",
    database=environ.get('MYSQL_DATABASE'),
    query={"charset":"utf8"}
)

ENGINE = create_engine(
    url,
    echo=True
)

def reset_database():
    UserBase.metadata.drop_all(bind=ENGINE)
    BookBase.metadata.drop_all(bind=ENGINE)
    ArchivedBookBase.metadata.drop_all(bind=ENGINE)

    UserBase.metadata.create_all(bind=ENGINE)
    BookBase.metadata.create_all(bind=ENGINE)
    ArchivedBookBase.metadata.create_all(bind=ENGINE)

if __name__ == "__main__":
    reset_database()
