from attrs import define

from basket_cqrs_contract import hints

from framework.cqrs.query.query import Query

from .query_response import BasketDTO

__all__ = ('BasketByIdQuery', )


@define
class BasketByIdQuery(Query[BasketDTO]):
    id: hints.CustomerBasketId
