from sqlalchemy import select
from sqlalchemy.orm import Session

from eshop import settings
from eshop.apps.test_app import hints

from framework.ddd.dto import DTO

from .api_router import api_router
from .models import Author, Book


@api_router.get('/index/')
def index():
    return {'hello': 'world'}


@api_router.get('/settings/')
def settings__get():
    from eshop.settings import SETTINGS

    return {'db_name': SETTINGS.db.name}


class BookDTO(DTO):

    title: str
    author_name: str


@api_router.get('/book/{id}/')
def book__get(id: hints.BookId) -> BookDTO:
    with Session(settings.SQLALCHEMY_ENGINE) as session:
        # yapf: disable
        stmt = select(
            Book.title.label('title'),
            Author.name.label('author_name'),
        ).select_from(
            Book,
        ).join(
            Author,
        ).where(
            Book.id == id,
        )
        # yapf: enable
        result = session.execute(stmt).one()._asdict()

    return BookDTO(title=result['title'], author_name=result['author_name'])
