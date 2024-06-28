from typing import List

from pydantic import BaseModel

from sqlalchemy import INTEGER
from sqlalchemy.orm import Mapped, mapped_column

from basket import hints
from basket.app_config import BasketAppConfig

from framework.sqlalchemy.dialects.postgres.pydantic_type import PydanticType

__all__ = ('CustomerBasketORM', )


class BasketItem(BaseModel):
    id: hints.BasketItemId
    product_id: hints.ProductId
    product_name: hints.ProductName
    unit_price: hints.Price
    quantity: hints.Quantity
    picture_url: hints.PictureUrl


class Data(BaseModel):
    basket_items: List[BasketItem]


class CustomerBasketORM(BasketAppConfig.get_sqlalchemy_base()):

    __tablename__ = 'customer_basket'

    # customer_basket лежит в документо-ориентированном виде
    buyer_id: Mapped[hints.BuyerId] = mapped_column(INTEGER, primary_key=True)
    data: Mapped[Data] = mapped_column(PydanticType(Data))
