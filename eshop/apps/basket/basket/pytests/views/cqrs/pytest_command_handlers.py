from mock import Mock, patch

import sqlalchemy.orm

from basket.infrastructure.persistence.postgres.customer_basket import (
    CustomerBasketORM,
    PostgresCustomerBasketRepository,
)
from basket.infrastructure.persistence.postgres.customer_basket.customer_basket_orm import (
    BasketItem,
    Data,
)
from basket.views.cqrs.command_handlers import UpdateCustomerBasketCommandHandler

from basket_cqrs_contract.command import UpdateCustomerBasketCommand
from basket_cqrs_contract.customer_basket_dto import BasketItemDTO, CustomerBasketDTO

from framework.for_pytests.sqlalchemy_session_mock import SqlalchemySessionMock
from framework.for_pytests.test_case import TestCase
from framework.for_pytests.test_class import TestClass
from framework.sqlalchemy import session_factory


class TestCaseSucess(TestCase['TestUpdateCustomerBasketCommandHandler__handle']):
    command: UpdateCustomerBasketCommand


def test_case_success() -> TestCaseSucess:
    command = UpdateCustomerBasketCommand(
        customer_basket=CustomerBasketDTO(
            buyer_id=1,
            basket_items=[
                BasketItemDTO(
                    id=1,
                    product_id=1,
                    product_name='product_name1',
                    unit_price=10,
                    quantity=10,
                    picture_url='picture_url1',
                ),
                BasketItemDTO(
                    id=2,
                    product_id=2,
                    product_name='product_name2',
                    unit_price=20,
                    quantity=20,
                    picture_url='picture_url2',
                ),
            ],
        ),
    )

    return TestCaseSucess(command=command)


class TestUpdateCustomerBasketCommandHandler__handle(TestClass[UpdateCustomerBasketCommandHandler]):
    @patch.object(sqlalchemy.orm, 'Session', SqlalchemySessionMock)
    @patch.object(session_factory, 'session_factory')
    @patch.object(PostgresCustomerBasketRepository, 'save')
    def test_case_success(
        self,
        mock__postgres_customer_basket_repository__save: Mock,
        mock__session_factory: Mock,
        test_case_success: TestCaseSucess,
    ):
        test_case = test_case_success

        UpdateCustomerBasketCommandHandler().handle(command=test_case.command)

        mock__postgres_customer_basket_repository__save.assert_called_once_with(
            customer_basket=CustomerBasketORM(
                buyer_id=1,
                data=Data(
                    basket_items=[
                        BasketItem(
                            id=1,
                            product_id=1,
                            product_name='product_name1',
                            unit_price=10,
                            quantity=10,
                            picture_url='picture_url1',
                        ),
                        BasketItem(
                            id=2,
                            product_id=2,
                            product_name='product_name2',
                            unit_price=20,
                            quantity=20,
                            picture_url='picture_url2',
                        ),
                    ],
                ),
            ),
        )

        SqlalchemySessionMock.commit.assert_called_once()
