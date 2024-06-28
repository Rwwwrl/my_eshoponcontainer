from typing import Optional, Type

from fastapi import APIRouter

from sqlalchemy.orm import DeclarativeBase

from framework.app_config import IAppConfig


class BasketAppConfig(IAppConfig):

    name = 'basket'

    @classmethod
    def get_api_router(cls) -> Optional[APIRouter]:
        return None

    @classmethod
    def get_sqlalchemy_base(cls) -> Optional[Type[DeclarativeBase]]:
        from .infrastructure.persistence.postgres.base import Base

        return Base

    @classmethod
    def import_models(cls) -> None:
        from .infrastructure.persistence.postgres import customer_basket    # noqa

    @classmethod
    def import_http_views(cls) -> None:
        pass

    @classmethod
    def import_cqrs_handlers(cls) -> None:
        from .views import cqrs    # noqa
