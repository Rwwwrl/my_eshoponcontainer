from typing import Annotated, Dict, List, Set

from fastapi import Depends, Response, status

import basket_cqrs_contract.hints
from basket_cqrs_contract.command import UpdateCustomerBasketCommand
from basket_cqrs_contract.customer_basket_dto import BasketItemDTO, CustomerBasketDTO
from basket_cqrs_contract.query.query import CustomerBasketQuery

from framework.cqrs.exceptions import CQRSException
from framework.fastapi.dependencies.get_user_from_request import get_user_from_http_request
from framework.fastapi.http_exceptions import BadRequestException
from framework.fastapi.http_exceptions import InternalServerError

import user_identity_cqrs_contract.hints

from .dto import UpdateBasketItemsRequest
from ..api_router import api_router

__all__ = ('update_quantities', )


class RequestDataIsInvalidBaseException(Exception):
    pass


class NoUpdatesSentError(RequestDataIsInvalidBaseException):
    pass


class RequestDataReferenceToNonExistingBasketItemsError(RequestDataIsInvalidBaseException):
    def __init__(self, *args, invalid_ids: List[basket_cqrs_contract.hints.BasketItemId], **kwargs):
        self.invalid_ids = invalid_ids


def _ensure_request_data_is_valid(request_data: UpdateBasketItemsRequest, customer_basket: CustomerBasketDTO) -> None:
    if not request_data.updates:
        raise NoUpdatesSentError

    # yapf: disable
    customer_basket_basket_items_ids: Set[basket_cqrs_contract.hints.BasketItemId] = set(
        [bi.id for bi in customer_basket.basket_items],
    )
    # yapf: enable

    invalid_ids: List[basket_cqrs_contract.hints.BasketItemId] = []
    for basket_item_update in request_data.updates:
        if basket_item_update.basket_item_id not in customer_basket_basket_items_ids:
            invalid_ids.append(basket_item_update.basket_item_id)

    if invalid_ids:
        raise RequestDataReferenceToNonExistingBasketItemsError(invalid_ids=invalid_ids)


@api_router.put('/basket/basket_items/')
def update_quantities(
    request_data: UpdateBasketItemsRequest,
    user_id: Annotated[
        user_identity_cqrs_contract.hints.UserId,
        Depends(get_user_from_http_request),
    ],
) -> Response:
    customer_basket = CustomerBasketQuery(customer_id=user_id).fetch()

    try:
        _ensure_request_data_is_valid(request_data=request_data, customer_basket=customer_basket)
    except NoUpdatesSentError:
        raise BadRequestException(detail='no updates sent')
    except RequestDataReferenceToNonExistingBasketItemsError as e:
        raise BadRequestException(
            detail=f'request data reference to non existing basket items, invalid ids: {e.invalid_ids}',
        )

    basket_item_id_to_new_quantity: Dict[basket_cqrs_contract.hints.BasketItemId, int] = {}
    for basket_item_update in request_data.updates:
        basket_item_id_to_new_quantity[basket_item_update.basket_item_id] = basket_item_update.new_quantity

    for i, basket_item in enumerate(customer_basket.basket_items):
        if basket_item.id in basket_item_id_to_new_quantity:
            customer_basket.basket_items[i] = BasketItemDTO(
                id=basket_item.id,
                product_id=basket_item.product_id,
                product_name=basket_item.product_name,
                unit_price=basket_item.unit_price,
                quantity=basket_item_id_to_new_quantity[basket_item.id],
                picture_url=basket_item.picture_url,
            )

    try:
        UpdateCustomerBasketCommand(customer_basket=customer_basket).execute()
    except CQRSException:
        raise InternalServerError(
            detail=f'failed to update basket due to {UpdateCustomerBasketCommand.__name__} failed',
        )

    return Response(status_code=status.HTTP_200_OK)
