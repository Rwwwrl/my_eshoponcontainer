from basket.infrastructure.persistence.postgres.customer_basket import (
    CustomerBasketORM,
    PostgresCustomerBasketRepository,
)
from basket.infrastructure.persistence.postgres.customer_basket.customer_basket_orm import (
    BasketItem,
    Data,
)

from basket_cqrs_contract.command import UpdateCustomerBasketCommand

from framework.cqrs.command import ICommandHandler
from framework.sqlalchemy.session_factory import session_factory


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
                        picture_url=basket_item.quantity,
                    ) for basket_item in command.customer_basket.basket_items
                ],
            ),
        )

    def handle(self, command: UpdateCustomerBasketCommand) -> None:
        customer_basket = self._deserialize_to_orm(command=command)
        with session_factory() as session:
            customer_basket_repository = PostgresCustomerBasketRepository(session=session)
            customer_basket_repository.save(customer_basket_orm=customer_basket)
            session.commit()
