from typing import Optional, Type

from fastapi import APIRouter

from sqlalchemy.orm import DeclarativeBase

from framework.iapp_config import IAppConfig


class UserIdentityAppConfig(IAppConfig):

    name = 'user_identity'

    @classmethod
    def get_api_router(cls) -> Optional[APIRouter]:
        from .api_router import api_router

        return api_router

    @classmethod
    def get_sqlalchemy_base(cls) -> Optional[Type[DeclarativeBase]]:
        from .infrastructure.peristance.base import Base

        return Base

    @classmethod
    def import_models(cls) -> None:
        from .infrastructure import peristance    # noqa

    @classmethod
    def import_http_views(cls) -> None:
        from .views import http    # noqa

    @classmethod
    def import_cqrs_handlers(cls) -> None:
        from .views import cqrs    # noqa
