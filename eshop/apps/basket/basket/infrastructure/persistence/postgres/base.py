from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from basket.app_config import BasketAppConfig


class Base(DeclarativeBase):

    metadata = MetaData(schema=BasketAppConfig.name)
