from collections import defaultdict
from typing import Annotated, Dict, Final, List, Set

from fastapi import Depends, status
from fastapi.responses import Response

from basket_cqrs_contract.command import UpdateCustomerBasketCommand
from basket_cqrs_contract.customer_basket_dto import BasketItemDTO, CustomerBasketDTO

import catalog_cqrs_contract.hints
from catalog_cqrs_contract.query import CatalogItemsByIdsQuery
from catalog_cqrs_contract.query.query_response import CatalogItemDTO

from framework.cqrs.exceptions import CQRSException
from framework.fastapi.dependencies.get_user_from_request import get_user_from_http_request
from framework.fastapi.http_exceptions import BadRequestException, InternalServerError

import user_identity_cqrs_contract.hints

from .dto import ProductId, UpdateBasketRequestData, UpdateBasketRequestItemData
from ..api_router import api_router

__all__ = ('update_basket', )


class BasketReferToNonExisingProducts(Exception):
    def __init__(self, *args, invalid_product_ids: List[ProductId], **kwargs):
        self.invalid_product_ids = invalid_product_ids


def _normalize_request_data(request_data: UpdateBasketRequestData) -> UpdateBasketRequestData:
    """
    группируем дату по `product_id` во избежание дубликатов
    """

    product_it_to_quantity: Dict[int, int] = defaultdict(float)

    for basket_item in request_data.basket_items:
        product_it_to_quantity[basket_item.product_id] += basket_item.quantity

    return UpdateBasketRequestData(
        buyer_id=request_data.buyer_id,
        basket_items=[
            UpdateBasketRequestItemData(
                product_id=product_id,
                quantity=quantity,
            ) for product_id, quantity in product_it_to_quantity.items()
        ],
    )


def _ensure_basket_refer_to_existing_products(
    request_data: UpdateBasketRequestData,
    existing_products_ids: Set[ProductId],
) -> None:
    invalid_product_ids: List[int] = []

    for product_id in [bi.product_id for bi in request_data.basket_items]:
        if product_id not in existing_products_ids:
            invalid_product_ids.append(product_id)

    if invalid_product_ids:
        raise BasketReferToNonExisingProducts(invalid_product_ids=invalid_product_ids)


@api_router.put('/basket/')
def update_basket(
    request_data: UpdateBasketRequestData,
    user_id: Annotated[
        user_identity_cqrs_contract.hints.UserId,
        Depends(get_user_from_http_request),
    ],
) -> Response:
    if not request_data.basket_items:
        raise BadRequestException(detail='basket must have at least one basket item')

    request_data = _normalize_request_data(request_data=request_data)
    request_data_product_ids: List[ProductId] = [bi.product_id for bi in request_data.basket_items]

    catalog_items = CatalogItemsByIdsQuery(ids=request_data_product_ids).fetch()
    catalog_items_identity_map: Dict[catalog_cqrs_contract.hints.CatalogItemId, CatalogItemDTO] = {
        item.id: item
        for item in catalog_items
    }

    try:
        _ensure_basket_refer_to_existing_products(
            request_data=request_data,
            existing_products_ids=set(ProductId(item.id) for item in catalog_items),
        )
    except BasketReferToNonExisingProducts as e:
        raise BadRequestException(
            detail=f'basket refer to non-existing products, invalid products: {e.invalid_product_ids}',
        )

    basket_items: Final[List[BasketItemDTO]] = []
    for basket_request_item_data in request_data.basket_items:
        catalog_item = catalog_items_identity_map[basket_request_item_data.product_id]
        basket_items.append(
            BasketItemDTO(
                id=None,
                product_id=basket_request_item_data.product_id,
                product_name=catalog_item.name,
                unit_price=catalog_item.price,
                quantity=basket_request_item_data.quantity,
                picture_url=catalog_item.picture_url,
            ),
        )

    try:
        UpdateCustomerBasketCommand(customer_basket=CustomerBasketDTO(
            buyer_id=user_id,
            basket_items=basket_items,
        )).execute()
    except CQRSException:
        raise InternalServerError(
            detail=f'failed to update basket due to {UpdateCustomerBasketCommand.__name__} failed',
        )

    return Response(status_code=status.HTTP_200_OK)
