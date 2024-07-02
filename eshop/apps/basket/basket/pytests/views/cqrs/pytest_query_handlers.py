from mock import Mock, patch

import pytest

from basket.infrastructure.persistence.postgres.customer_basket import (
    CustomerBasketORM,
    PostgresCustomerBasketRepository,
)
from basket.infrastructure.persistence.postgres.customer_basket.customer_basket_orm import (
    BasketItem,
    Data,
)
from basket.views.cqrs.query_handlers import CustomerBasketQueryHandler

from basket_cqrs_contract.customer_basket_dto import BasketItemDTO, CustomerBasketDTO
from basket_cqrs_contract.query import CustomerBasketQuery

from framework.for_pytests.test_case import TestCase
from framework.for_pytests.test_class import TestClass


class BasketByIdQueryHandler__handleTestCase(TestCase['TestBasketByIdQueryHandler__handle']):
    query: CustomerBasketQuery
    mock_customer_basket_repository_get_by_id_return_value: CustomerBasketORM
    expected_result: CustomerBasketDTO


@pytest.fixture(scope='session')
def use_case_basket_by_id_query_handler__handle() -> BasketByIdQueryHandler__handleTestCase:
    query = CustomerBasketQuery(customer_id=1)
    mock_repository_get_by_id_return_value = CustomerBasketORM(
        buyer_id=10,
        data=Data(
            basket_items=[
                BasketItem(
                    id=1,
                    product_id=1,
                    product_name='product_name1',
                    unit_price=10,
                    quantity=3,
                    picture_url='picture_url1',
                ),
                BasketItem(
                    id=2,
                    product_id=3,
                    product_name='product_name2',
                    unit_price=15,
                    quantity=2,
                    picture_url='picture_url2',
                ),
            ],
        ),
    )

    expected_result = CustomerBasketDTO(
        buyer_id=10,
        basket_items=[
            BasketItemDTO(
                id=1,
                product_id=2,
                product_name='product_name1',
                unit_price=10,
                quantity=3,
                picture_url='picture_url1',
            ),
            BasketItemDTO(
                id=2,
                product_id=3,
                product_name='product_name2',
                unit_price=15,
                quantity=2,
                picture_url='picture_url2',
            ),
        ],
    )

    return BasketByIdQueryHandler__handleTestCase(
        query=query,
        mock_customer_basket_repository_get_by_id_return_value=mock_repository_get_by_id_return_value,
        expected_result=expected_result,
    )


class TestBasketByIdQueryHandler__handle(TestClass[CustomerBasketQueryHandler.handle]):
    @patch.object(PostgresCustomerBasketRepository, 'get_by_buyer_id')
    def test(
        self,
        mock__customer_basket_repository__get_by_buyer_id: Mock,
        use_case_basket_by_id_query_handler__handle: BasketByIdQueryHandler__handleTestCase,
    ):
        use_case = use_case_basket_by_id_query_handler__handle

        mock__customer_basket_repository__get_by_buyer_id.return_value = (
            use_case.mock_customer_basket_repository_get_by_id_return_value
        )

        result = CustomerBasketQueryHandler().handle(query=use_case.query)
        assert use_case.expected_result == result
