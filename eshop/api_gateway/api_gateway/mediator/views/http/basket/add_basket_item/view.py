from typing import Annotated, List

from fastapi import Depends, Response, status

from basket_cqrs_contract.command import UpdateCustomerBasketCommand
from basket_cqrs_contract.customer_basket_dto import BasketItemDTO, CustomerBasketDTO
from basket_cqrs_contract.query import CustomerBasketQuery

from catalog_cqrs_contract.query import CatalogItemsByIdsQuery

from framework.cqrs.exceptions import CQRSException
from framework.fastapi.dependencies.get_user_from_request import get_user_from_http_request
from framework.fastapi.http_exceptions import InternalServerError

import user_identity_cqrs_contract.hints

from .dto import AddBasketItemRequest
from ..api_router import api_router

__all__ = ('add_basket_item', )


@api_router.post('/basket/basket_items/')
def add_basket_item(
    request_data: AddBasketItemRequest,
    user_id: Annotated[
        user_identity_cqrs_contract.hints.UserId,
        Depends(get_user_from_http_request),
    ],
) -> Response:
    """
    добавляем продукт в корзину:
    1. в случае, если продукт уже есть в корзине, то просто увеличиваем его количество
    2. в случае, если продуакту еще нет, то добавляем его в корзину
    """

    customer_basket = CustomerBasketQuery(customer_id=user_id).fetch()

    try:
        basket_item = next(filter(lambda bi: bi.id == request_data.catalog_item_id, customer_basket.basket_items))
    except StopIteration:
        catalog_item = CatalogItemsByIdsQuery(ids=[request_data.catalog_item_id]).fetch()[0]
        new_basket_item = BasketItemDTO(
            id=None,
            product_id=catalog_item.id,
            product_name=catalog_item.name,
            unit_price=catalog_item.price,
            quantity=request_data.quantity,
            picture_url=catalog_item.picture_url,
        )
        basket_items: List[BasketItemDTO] = [new_basket_item, *customer_basket.basket_items]

    else:
        updated_basket_item = BasketItemDTO(
            id=basket_item.id,
            product_id=basket_item.product_id,
            product_name=basket_item.product_name,
            unit_price=basket_item.unit_price,
            quantity=basket_item.quantity + request_data.quantity,
            picture_url=basket_item.picture_url,
        )
        basket_items: List[BasketItemDTO] = [
            updated_basket_item,
            *filter(lambda bi: bi.id != updated_basket_item.id, customer_basket.basket_items),
        ]

    try:
        UpdateCustomerBasketCommand(
            customer_basket=CustomerBasketDTO(
                buyer_id=customer_basket.buyer_id,
                basket_items=basket_items,
            ),
        ).execute()
    except CQRSException:
        raise InternalServerError(
            detail=f'failed to update basket due to {UpdateCustomerBasketCommand.__name__} failed',
        )

    return Response(status_code=status.HTTP_200_OK)
