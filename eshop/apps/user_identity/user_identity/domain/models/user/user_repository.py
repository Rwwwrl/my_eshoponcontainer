from sqlalchemy import select
from sqlalchemy.orm import Session

from user_identity import hints

from .user import User

__all__ = ('UserRepository', )


class NotFoundError(Exception):
    pass


class UserRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, id: hints.UserId) -> User:
        stmt = select(User).where(User.id == id)

        user = self._session.scalar(stmt)
        if not user:
            raise NotFoundError(f'user with id = {id} does not exist')

        self._session.expunge(user)

        return user

    def get_by_name(self, name: hints.UserName) -> User:
        stmt = select(User).where(User.name == name)

        user = self._session.scalar(stmt)
        if not user:
            raise NotFoundError(f'user with name = {name} does not exist')

        self._session.expunge(user)

        return user
