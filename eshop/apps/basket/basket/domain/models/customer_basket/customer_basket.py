from typing import List

from pydantic import BaseModel

from basket import hints

__all__ = ('CustomerBasket', )


class BasketItem(BaseModel):
    id: hints.BasketItemId
    basket_pk: hints.BuyerId
    product_id: hints.ProductId
    product_name: hints.ProductName
    unit_price: hints.Price
    quantity: hints.Quantity
    picture_url: hints.PictureUrl


class CustomerBasket(BaseModel):

    buyer_id: hints.BuyerId
    basket_items: List[BasketItem]
