from __future__ import annotations

from typing import List, TYPE_CHECKING

from sqlalchemy import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from basket import hints
from basket.app_config import BasketAppConfig

if TYPE_CHECKING:
    from ..basket_item import BasketItem


class CustomerBasket(BasketAppConfig.get_sqlalchemy_base()):

    __tablename__ = 'customer_basket'

    buyer_id: Mapped[hints.CustomerId] = mapped_column(INTEGER, primary_key=True)

    basket_items: Mapped[List[BasketItem]] = relationship(back_populates='basket')
