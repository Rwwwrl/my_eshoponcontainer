from typing import Optional, Type

from fastapi import APIRouter

from sqlalchemy.orm import DeclarativeBase

from framework.iapp_config import IAppConfig


class TestAppConfig(IAppConfig):

    name = 'test_app'

    @classmethod
    def get_api_router(cls) -> Optional[APIRouter]:
        from .api_router import api_router

        return api_router

    @classmethod
    def get_sqlalchemy_base(cls) -> Optional[Type[DeclarativeBase]]:
        from .models import Base

        return Base

    @classmethod
    def import_models(cls) -> None:
        from . import models    # noqa

    @classmethod
    def import_http_views(cls) -> None:
        from . import views    # noqa

    @classmethod
    def import_cqrs_handlers(cls) -> None:
        pass
