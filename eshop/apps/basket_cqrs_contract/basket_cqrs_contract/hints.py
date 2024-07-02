from typing import NewType

from pydantic.types import PositiveFloat, PositiveInt

CustomerId = NewType('CustomerId', PositiveInt)
BuyerId = NewType('BuyerId', CustomerId)

BasketItemId = NewType('BasketItemId', PositiveInt)
ProductId = NewType('ProductId', PositiveInt)
ProductName = NewType('ProductName', str)
Price = NewType('Price', PositiveFloat)
Quantity = NewType('Quantity', PositiveInt)
PictureUrl = NewType('PictureUrl', str)
