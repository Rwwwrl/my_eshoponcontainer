from typing import List, NewType, final

from pydantic.types import PositiveInt

from framework.common.dto import DTO

ProductId = NewType('ProductId', PositiveInt)


@final
class UpdateBasketRequestItemData(DTO):
    product_id: ProductId
    quantity: PositiveInt


@final
class UpdateBasketRequestData(DTO):
    buyer_id: PositiveInt
    basket_items: List[UpdateBasketRequestItemData]
