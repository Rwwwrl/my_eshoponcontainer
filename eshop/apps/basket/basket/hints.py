from typing import NewType

from pydantic.types import PositiveFloat, PositiveInt

BuyerId = NewType('BuyerId', PositiveInt)
CustomerBasketPK = NewType('CustomerBasketPK', BuyerId)

BasketItemId = NewType('BasketItemId', PositiveInt)
ProductId = NewType('ProductId', PositiveInt)

ProductName = NewType('ProductName', str)
Price = NewType('Price', PositiveFloat)
Quantity = NewType('Quantity', PositiveInt)
PictureUrl = NewType('PictureUrl', str)
