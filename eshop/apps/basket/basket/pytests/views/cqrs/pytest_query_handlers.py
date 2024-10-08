from mock import Mock, patch

import pytest

from basket.domain.models.customer_basket import (
    CustomerBasketORM,
    PostgresCustomerBasketRepository,
)
from basket.domain.models.customer_basket.customer_basket import (
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
    mock__customer_basket_repository__get_by_id__return_value: CustomerBasketORM
    expected_result: CustomerBasketDTO


@pytest.fixture(scope='session')
def test_case_basket_by_id_query_handler__handle() -> BasketByIdQueryHandler__handleTestCase:
    query = CustomerBasketQuery(customer_id=1)
    mock_repository_get_by_id_return_value = CustomerBasketORM(
        buyer_id=1,
        data=Data(
            basket_items=[
                BasketItem(
                    id=1,
                    product_id=1,
                    product_name='product_name1',
                    unit_price=10,
                    quantity=3,
                    discount=10,
                    picture_url='picture_url1',
                ),
                BasketItem(
                    id=2,
                    product_id=2,
                    product_name='product_name2',
                    unit_price=15,
                    quantity=2,
                    discount=15,
                    picture_url='picture_url2',
                ),
            ],
        ),
    )

    expected_result = CustomerBasketDTO(
        buyer_id=1,
        basket_items=[
            BasketItemDTO(
                id=1,
                product_id=1,
                product_name='product_name1',
                unit_price=10,
                quantity=3,
                discount=10,
                picture_url='picture_url1',
            ),
            BasketItemDTO(
                id=2,
                product_id=2,
                product_name='product_name2',
                unit_price=15,
                quantity=2,
                discount=15,
                picture_url='picture_url2',
            ),
        ],
    )

    return BasketByIdQueryHandler__handleTestCase(
        query=query,
        mock__customer_basket_repository__get_by_id__return_value=mock_repository_get_by_id_return_value,
        expected_result=expected_result,
    )


class TestBasketByIdQueryHandler__handle(TestClass[CustomerBasketQueryHandler.handle]):
    @patch.object(PostgresCustomerBasketRepository, 'get_by_buyer_id')
    def test(
        self,
        mock__customer_basket_repository__get_by_buyer_id: Mock,
        test_case_basket_by_id_query_handler__handle: BasketByIdQueryHandler__handleTestCase,
    ):
        test_case = test_case_basket_by_id_query_handler__handle

        mock__customer_basket_repository__get_by_buyer_id.return_value = (
            test_case.mock__customer_basket_repository__get_by_id__return_value
        )

        result = CustomerBasketQueryHandler().handle(query=test_case.query)
        assert result == test_case.expected_result

        mock__customer_basket_repository__get_by_buyer_id.assert_called_once_with(
            buyer_id=test_case.query.customer_id,
        )
