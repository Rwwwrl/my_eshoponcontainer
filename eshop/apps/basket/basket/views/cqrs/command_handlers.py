from basket.domain.models.customer_basket import (
    CustomerBasketORM,
    PostgresCustomerBasketRepository,
)
from basket.domain.models.customer_basket.customer_basket import (
    BasketItem,
    Data,
)

from basket_cqrs_contract.command import UpdateCustomerBasketCommand

from framework.cqrs.command import ICommandHandler
from framework.sqlalchemy.session import Session


@UpdateCustomerBasketCommand.handler
class UpdateCustomerBasketCommandHandler(ICommandHandler):
    @staticmethod
    def _deserialize_to_orm(command: UpdateCustomerBasketCommand) -> CustomerBasketORM:
        return CustomerBasketORM(
            buyer_id=command.customer_basket.buyer_id,
            data=Data(
                basket_items=[
                    BasketItem(
                        id=basket_item.id,
                        product_id=basket_item.product_id,
                        product_name=basket_item.product_name,
                        unit_price=basket_item.unit_price,
                        quantity=basket_item.quantity,
                        picture_url=basket_item.picture_url,
                        discount=basket_item.discount,
                    ) for basket_item in command.customer_basket.basket_items
                ],
            ),
        )

    def handle(self, command: UpdateCustomerBasketCommand) -> None:
        customer_basket_orm = self._deserialize_to_orm(command=command)
        with Session() as session:
            customer_basket_repository = PostgresCustomerBasketRepository(session=session)
            with session.begin():
                customer_basket_repository.save(customer_basket_orm=customer_basket_orm)
