from typing import Annotated, List

from fastapi import Depends

from basket.api_router import api_router
from basket.infrastructure.persistence.postgres.customer_basket import CustomerBasketORM
from basket.infrastructure.persistence.postgres.customer_basket.postgres_customer_basket_repository import (
    NotFoundError,
    PostgresCustomerBasketRepository,
)

from framework.fastapi.dependencies.get_user_from_request import get_user_from_http_request
from framework.sqlalchemy.session_factory import session_factory

from user_identity_cqrs_contract.hints import UserId

from .dto import BasketItemDTO, CustomerBasketDTO

__all__ = ('get_customer_basket', )


def _orm_to_dto(customer_basket_orm: CustomerBasketORM) -> CustomerBasketDTO:
    basket_items: List[BasketItemDTO] = []
    for basket_item in customer_basket_orm.data.basket_items:
        basket_items.append(
            BasketItemDTO(
                id=basket_item.id,
                product_id=basket_item.product_id,
                product_name=basket_item.product_name,
                unit_price=basket_item.unit_price,
                quantity=basket_item.quantity,
                picture_url=basket_item.picture_url,
            ),
        )

    return CustomerBasketDTO(
        buyer_id=customer_basket_orm.buyer_id,
        basket_items=basket_items,
    )


@api_router.get('/customer_basket/')
def get_customer_basket(user_id: Annotated[UserId, Depends(get_user_from_http_request)]) -> CustomerBasketDTO:
    with session_factory() as session:
        customer_basket_repository = PostgresCustomerBasketRepository(session=session)

        try:
            customer_basket_orm = customer_basket_repository.get_by_buyer_id(buyer_id=user_id)
        except NotFoundError:
            customer_basket_orm = customer_basket_repository.create(buyer_id=user_id)
            session.expunge(customer_basket_orm)
            session.commit()

    return _orm_to_dto(customer_basket_orm=customer_basket_orm)
