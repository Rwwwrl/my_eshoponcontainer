from mock import MagicMock, Mock, patch

import pytest

from basket.app_config import BasketAppConfig
from basket.domain.models.customer_basket.customer_basket import (
    BasketItem,
    CustomerBasketORM,
    Data,
)
from basket.domain.models.customer_basket.customer_basket_repository import (
    NotFoundError,
    PostgresCustomerBasketRepository,
)
from basket.views.http.get_customer_basket import get_customer_basket
from basket.views.http.get_customer_basket import view
from basket.views.http.get_customer_basket.dto import BasketItemDTO, CustomerBasketDTO

from framework.for_pytests.test_case import TestCase
from framework.for_pytests.test_class import TestClass
from framework.sqlalchemy.session import Session

from user_identity_cqrs_contract.hints import UserId


class TestCaseUserHaveBasket(TestCase):

    user_id: UserId
    mock__customer_basket_repository__get_by_buyer_id__return_value: CustomerBasketORM
    expected_response: CustomerBasketDTO


class TestCaseUserDoesNotHaveBasket(TestCase):

    user_id: UserId
    expected_response: CustomerBasketDTO
    mock__customer_basket_repository__create__return_value: CustomerBasketORM


@pytest.fixture(scope='session')
def test_case_user_have_basket() -> TestCaseUserHaveBasket:
    user_id = 1

    mock__customer_basket_repository__get_by_buyer_id__return_value = CustomerBasketORM(
        buyer_id=1,
        data=Data(
            basket_items=[
                BasketItem(
                    id=1,
                    product_id=1,
                    product_name='product_name1',
                    unit_price=10,
                    quantity=1,
                    picture_url='picture_url1',
                    discount=10,
                ),
                BasketItem(
                    id=2,
                    product_id=2,
                    product_name='product_name2',
                    unit_price=10,
                    quantity=1,
                    picture_url='picture_url2',
                    discount=12,
                ),
            ],
        ),
    )

    expected_response = CustomerBasketDTO(
        buyer_id=1,
        basket_items=[
            BasketItemDTO(
                id=1,
                product_id=1,
                product_name='product_name1',
                unit_price=10,
                quantity=1,
                picture_url='picture_url1',
                discount=10,
            ),
            BasketItemDTO(
                id=2,
                product_id=2,
                product_name='product_name2',
                unit_price=10,
                quantity=1,
                picture_url='picture_url2',
                discount=12,
            ),
        ],
    )

    return TestCaseUserHaveBasket(
        user_id=user_id,
        mock__customer_basket_repository__get_by_buyer_id__return_value=(
            mock__customer_basket_repository__get_by_buyer_id__return_value
        ),
        expected_response=expected_response,
    )


@pytest.fixture(scope='session')
def test_case_user_does_not_have_basket() -> TestCaseUserDoesNotHaveBasket:
    user_id = 1

    expected_response = CustomerBasketDTO(
        buyer_id=1,
        basket_items=[],
    )

    mock__customer_basket_repository__create__return_value = CustomerBasketORM(
        buyer_id=1,
        data=Data(basket_items=[]),
    )

    return TestCaseUserDoesNotHaveBasket(
        user_id=user_id,
        expected_response=expected_response,
        mock__customer_basket_repository__create__return_value=mock__customer_basket_repository__create__return_value,
    )


class TestUrlToView(TestClass[get_customer_basket]):
    def test(self):
        expected_url = '/basket/customer_basket/'
        fact_url = BasketAppConfig.get_api_router().url_path_for(get_customer_basket.__name__)
        assert fact_url == expected_url


class TestGetCustomerBasketView(TestClass[get_customer_basket]):
    @patch.object(PostgresCustomerBasketRepository, PostgresCustomerBasketRepository.get_by_buyer_id.__name__)
    def test_case_user_have_basket(
        self,
        mock__customer_basket_repository__get_by_buyer_id: Mock,
        test_case_user_have_basket: TestCaseUserHaveBasket,
    ):
        test_case = test_case_user_have_basket

        mock__customer_basket_repository__get_by_buyer_id.return_value = (
            test_case.mock__customer_basket_repository__get_by_buyer_id__return_value
        )

        response = get_customer_basket(user_id=test_case.user_id)
        assert response == test_case.expected_response

        mock__customer_basket_repository__get_by_buyer_id.assert_called_once_with(buyer_id=test_case.user_id)

    @patch.object(view, 'Session', new=MagicMock(spec=Session))
    @patch.object(PostgresCustomerBasketRepository, PostgresCustomerBasketRepository.create.__name__)
    @patch.object(PostgresCustomerBasketRepository, PostgresCustomerBasketRepository.get_by_buyer_id.__name__)
    def test_case_user_does_not_have_basket(
        self,
        mock__customer_basket_repository__get_by_buyer_id: Mock,
        mock__customer_basket_repository__create: Mock,
        test_case_user_does_not_have_basket: TestCaseUserDoesNotHaveBasket,
    ):
        test_case = test_case_user_does_not_have_basket

        mock__customer_basket_repository__get_by_buyer_id.side_effect = NotFoundError

        mock__customer_basket_repository__create.return_value = (
            test_case.mock__customer_basket_repository__create__return_value
        )

        response = get_customer_basket(user_id=test_case.user_id)
        assert response == test_case.expected_response

        mock__customer_basket_repository__get_by_buyer_id.assert_called_once_with(buyer_id=test_case.user_id)

        mock__customer_basket_repository__create.assert_called_once_with(buyer_id=test_case.user_id)
