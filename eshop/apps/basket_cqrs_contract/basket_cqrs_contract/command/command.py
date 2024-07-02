from typing import final

from attrs import define

from basket_cqrs_contract.customer_basket_dto import CustomerBasketDTO

from framework.cqrs.command import Command

__all__ = ('UpdateCustomerBasketCommand', )


@final
@define
class UpdateCustomerBasketCommand(Command[None]):

    customer_basket: CustomerBasketDTO
