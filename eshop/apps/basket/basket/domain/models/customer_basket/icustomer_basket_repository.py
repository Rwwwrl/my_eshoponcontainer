import abc

from basket import hints

from . import CustomerBasket

__all__ = ('ICustomerBasketRepository', )


class ICustomerBasketRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_buyer_id(self, buyer_id: hints.BuyerId) -> CustomerBasket:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, customer_basket: CustomerBasket) -> None:
        raise NotImplementedError
