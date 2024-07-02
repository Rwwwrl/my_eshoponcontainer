from typing import Any, List, cast

from fastapi import HTTPException, status

from mock import Mock, patch

import pytest

from typing_extensions import TypedDict

from api_gateway.mediator.views.http.basket.add_basket_item import add_basket_item
from api_gateway.mediator.views.http.basket.add_basket_item.dto import AddBasketItemRequest

from basket_cqrs_contract.command import UpdateCustomerBasketCommand
from basket_cqrs_contract.customer_basket_dto import BasketItemDTO, CustomerBasketDTO
from basket_cqrs_contract.query import CustomerBasketQuery

import catalog_cqrs_contract.query.query_response
from catalog_cqrs_contract.query import CatalogItemsByIdsQuery

from framework.cqrs.exceptions import CQRSException
from framework.for_pytests.for_testing_http_views import ExpectedHttpResponse, ExpectedHttpResponseException
from framework.for_pytests.test_case import TestCase
from framework.for_pytests.test_class import TestClass

import user_identity_cqrs_contract.hints


class ExpectedUpdateCustomerBasketCommandInitCallArgs(TypedDict):
    customer_basket: CustomerBasketDTO


class TestCaseBasketDoesNotHaveBasketItem(TestCase['TestViewAddBasketItem']):
    request_data: AddBasketItemRequest
    user_id: user_identity_cqrs_contract.hints.UserId
    mock__customer_basket_query__fetch__return_value: CustomerBasketDTO
    mock__catalog_items_by_ids_query__fetch__return_value: List[
        catalog_cqrs_contract.query.query_response.CatalogItemDTO]
    expected_update_customer_basket_command_init_call_args: ExpectedUpdateCustomerBasketCommandInitCallArgs
    expected_http_response: ExpectedHttpResponse


class TestCaseBasketAlreadyHaveBasketItem(TestCase['TestViewAddBasketItem']):
    request_data: AddBasketItemRequest
    user_id: user_identity_cqrs_contract.hints.UserId
    mock__customer_basket_query__fetch__return_value: CustomerBasketDTO
    expected_update_customer_basket_command_init_call_args: ExpectedUpdateCustomerBasketCommandInitCallArgs
    expected_http_response: ExpectedHttpResponse


class TestCaseUpdateCustomerBasketCommandExecuteCqrsException(TestCase['TestViewAddBasketItem']):
    request_data: AddBasketItemRequest
    user_id: user_identity_cqrs_contract.hints.UserId
    mock__customer_basket_query__fetch__return_value: CustomerBasketDTO
    expected_update_customer_basket_command_init_call_args: ExpectedUpdateCustomerBasketCommandInitCallArgs
    expected_http_response_exception: ExpectedHttpResponseException


@pytest.fixture(scope='session')
def test_case_basket_does_not_have_basket_item() -> TestCaseBasketDoesNotHaveBasketItem:
    request_data = AddBasketItemRequest(
        catalog_item_id=3,
        quantity=3,
    )

    user_id = 1

    mock__customer_basket_query__fetch__return_value = CustomerBasketDTO(
        buyer_id=1,
        basket_items=[
            BasketItemDTO(
                id=1,
                product_id=1,
                product_name='product_name1',
                unit_price=10,
                quantity=5,
                picture_url='picture_url1',
            ),
            BasketItemDTO(
                id=2,
                product_id=2,
                product_name='product_name2',
                unit_price=20,
                quantity=1,
                picture_url='picture_url2',
            ),
        ],
    )

    mock__catalog_items_by_ids_query__fetch__return_value = [
        catalog_cqrs_contract.query.query_response.CatalogItemDTO(
            id=3,
            name='product_name3',
            description='description',
            price=10,
            picture_filename='picture_filename',
            picture_url='picture_url3',
            catalog_type=catalog_cqrs_contract.query.query_response.CatalogTypeDTO(
                id=1,
                type='type',
            ),
            catalog_brand=catalog_cqrs_contract.query.query_response.CatalogBrandDTO(
                id=1,
                brand='brand',
            ),
            available_stock=10,
            maxstock_threshold=15,
            on_reorder=False,
            restock_threshold=13,
        ),
    ]

    expected_update_customer_basket_command_init_call_args: ExpectedUpdateCustomerBasketCommandInitCallArgs = {
        'customer_basket':
            CustomerBasketDTO(
                buyer_id=1,
                basket_items=[
                    BasketItemDTO(
                        id=1,
                        product_id=1,
                        product_name='product_name1',
                        unit_price=10,
                        quantity=5,
                        picture_url='picture_url1',
                    ),
                    BasketItemDTO(
                        id=2,
                        product_id=2,
                        product_name='product_name2',
                        unit_price=20,
                        quantity=1,
                        picture_url='picture_url2',
                    ),
                    BasketItemDTO(
                        id=None,
                        product_id=3,
                        product_name='product_name3',
                        unit_price=10,
                        quantity=3,
                        picture_url='picture_url3',
                    ),
                ],
            ),
    }

    return TestCaseBasketDoesNotHaveBasketItem(
        request_data=request_data,
        user_id=user_id,
        mock__customer_basket_query__fetch__return_value=mock__customer_basket_query__fetch__return_value,
        mock__catalog_items_by_ids_query__fetch__return_value=mock__catalog_items_by_ids_query__fetch__return_value,
        expected_update_customer_basket_command_init_call_args=expected_update_customer_basket_command_init_call_args,
        expected_http_response=ExpectedHttpResponse(
            status_code=status.HTTP_200_OK,
            body=b'',
        ),
    )


@pytest.fixture(scope='session')
def test_case_basket_already_have_basket_item() -> TestCaseBasketAlreadyHaveBasketItem:
    request_data = AddBasketItemRequest(
        catalog_item_id=1,
        quantity=3,
    )

    user_id = 1

    mock__customer_basket_query__fetch__return_value = CustomerBasketDTO(
        buyer_id=1,
        basket_items=[
            BasketItemDTO(
                id=1,
                product_id=1,
                product_name='product_name1',
                unit_price=10,
                quantity=5,
                picture_url='picture_url1',
            ),
            BasketItemDTO(
                id=2,
                product_id=2,
                product_name='product_name2',
                unit_price=20,
                quantity=1,
                picture_url='picture_url2',
            ),
        ],
    )

    expected_update_customer_basket_command_init_call_args: ExpectedUpdateCustomerBasketCommandInitCallArgs = {
        'customer_basket':
            CustomerBasketDTO(
                buyer_id=1,
                basket_items=[
                    BasketItemDTO(
                        id=1,
                        product_id=1,
                        product_name='product_name1',
                        unit_price=10,
                        quantity=8,
                        picture_url='picture_url1',
                    ),
                    BasketItemDTO(
                        id=2,
                        product_id=2,
                        product_name='product_name2',
                        unit_price=20,
                        quantity=1,
                        picture_url='picture_url2',
                    ),
                ],
            ),
    }

    return TestCaseBasketAlreadyHaveBasketItem(
        request_data=request_data,
        user_id=user_id,
        mock__customer_basket_query__fetch__return_value=mock__customer_basket_query__fetch__return_value,
        expected_update_customer_basket_command_init_call_args=expected_update_customer_basket_command_init_call_args,
        expected_http_response=ExpectedHttpResponse(
            status_code=status.HTTP_200_OK,
            body=b'',
        ),
    )


@pytest.fixture(scope='session')
def test_case_update_customer_basket_command_execute_cqrs_exception() -> TestCaseBasketAlreadyHaveBasketItem:
    request_data = AddBasketItemRequest(
        catalog_item_id=1,
        quantity=3,
    )

    user_id = 1

    mock__customer_basket_query__fetch__return_value = CustomerBasketDTO(
        buyer_id=1,
        basket_items=[
            BasketItemDTO(
                id=1,
                product_id=1,
                product_name='product_name1',
                unit_price=10,
                quantity=5,
                picture_url='picture_url1',
            ),
            BasketItemDTO(
                id=2,
                product_id=2,
                product_name='product_name2',
                unit_price=20,
                quantity=1,
                picture_url='picture_url2',
            ),
        ],
    )

    expected_update_customer_basket_command_init_call_args: ExpectedUpdateCustomerBasketCommandInitCallArgs = {
        'customer_basket':
            CustomerBasketDTO(
                buyer_id=1,
                basket_items=[
                    BasketItemDTO(
                        id=1,
                        product_id=1,
                        product_name='product_name1',
                        unit_price=10,
                        quantity=8,
                        picture_url='picture_url1',
                    ),
                    BasketItemDTO(
                        id=2,
                        product_id=2,
                        product_name='product_name2',
                        unit_price=20,
                        quantity=1,
                        picture_url='picture_url2',
                    ),
                ],
            ),
    }

    return TestCaseUpdateCustomerBasketCommandExecuteCqrsException(
        request_data=request_data,
        user_id=user_id,
        mock__customer_basket_query__fetch__return_value=mock__customer_basket_query__fetch__return_value,
        expected_update_customer_basket_command_init_call_args=expected_update_customer_basket_command_init_call_args,
        expected_http_response_exception=ExpectedHttpResponseException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'failed to update basket due to {UpdateCustomerBasketCommand.__name__} failed',
        ),
    )


class TestViewAddBasketItem(TestClass[add_basket_item]):
    @staticmethod
    def _assert(fact: Any, expected: Any) -> None:
        assert fact == expected

    @patch.object(UpdateCustomerBasketCommand, '__init__')
    @patch.object(UpdateCustomerBasketCommand, 'execute')
    @patch.object(CatalogItemsByIdsQuery, 'fetch')
    @patch.object(CustomerBasketQuery, 'fetch')
    def test_case_basket_does_not_have_basket_item(
        self,
        mock__customer_basket_query__fetch: Mock,
        mock__catalog_items_by_ids_query__fetch: Mock,
        mock__update_customer_basket_command__execute: Mock,
        mock__update_customer_basket_command__init: Mock,
        test_case_basket_does_not_have_basket_item: TestCaseBasketDoesNotHaveBasketItem,
    ):
        test_case = test_case_basket_does_not_have_basket_item

        mock__customer_basket_query__fetch.return_value = test_case.mock__customer_basket_query__fetch__return_value

        mock__catalog_items_by_ids_query__fetch.return_value = (
            test_case.mock__catalog_items_by_ids_query__fetch__return_value
        )

        mock__update_customer_basket_command__execute.return_value = None
        mock__update_customer_basket_command__init.return_value = None

        response = add_basket_item(request_data=test_case.request_data, user_id=test_case.user_id)
        assert response.status_code == test_case.expected_http_response.status_code
        assert response.body == test_case.expected_http_response.body

        call = mock__update_customer_basket_command__init.call_args_list[0]
        call_kwargs__customer_basket_arg = cast(CustomerBasketDTO, call._get_call_arguments()[1]['customer_basket'])
        expected_customer_basket_arg = (
            test_case.expected_update_customer_basket_command_init_call_args['customer_basket']
        )
        assert call_kwargs__customer_basket_arg.buyer_id == expected_customer_basket_arg.buyer_id
        self._assert(
            set(call_kwargs__customer_basket_arg.basket_items),
            set(expected_customer_basket_arg.basket_items),
        )
        mock__update_customer_basket_command__execute.assert_called_once()

    @patch.object(UpdateCustomerBasketCommand, '__init__')
    @patch.object(UpdateCustomerBasketCommand, 'execute')
    @patch.object(CustomerBasketQuery, 'fetch')
    def test_case_basket_already_have_basket_item(
        self,
        mock__customer_basket_query__fetch: Mock,
        mock__update_customer_basket_command__execute: Mock,
        mock__update_customer_basket_command__init: Mock,
        test_case_basket_already_have_basket_item: TestCaseBasketAlreadyHaveBasketItem,
    ):
        test_case = test_case_basket_already_have_basket_item

        mock__customer_basket_query__fetch.return_value = test_case.mock__customer_basket_query__fetch__return_value

        mock__update_customer_basket_command__execute.return_value = None
        mock__update_customer_basket_command__init.return_value = None

        response = add_basket_item(request_data=test_case.request_data, user_id=test_case.user_id)
        assert response.status_code == test_case.expected_http_response.status_code
        assert response.body == test_case.expected_http_response.body

        call = mock__update_customer_basket_command__init.call_args_list[0]
        call_kwargs__customer_basket_arg = cast(CustomerBasketDTO, call._get_call_arguments()[1]['customer_basket'])
        expected_customer_basket_arg = (
            test_case.expected_update_customer_basket_command_init_call_args['customer_basket']
        )
        assert call_kwargs__customer_basket_arg.buyer_id == expected_customer_basket_arg.buyer_id
        self._assert(
            set(call_kwargs__customer_basket_arg.basket_items),
            set(expected_customer_basket_arg.basket_items),
        )
        mock__update_customer_basket_command__execute.assert_called_once()

    @patch.object(UpdateCustomerBasketCommand, '__init__')
    @patch.object(UpdateCustomerBasketCommand, 'execute')
    @patch.object(CustomerBasketQuery, 'fetch')
    def test_case_update_customer_basket_command_execute_cqrs_exception(
        self,
        mock__customer_basket_query__fetch: Mock,
        mock__update_customer_basket_command__execute: Mock,
        mock__update_customer_basket_command__init: Mock,
        test_case_update_customer_basket_command_execute_cqrs_exception:
        TestCaseUpdateCustomerBasketCommandExecuteCqrsException,
    ):
        test_case = test_case_update_customer_basket_command_execute_cqrs_exception

        mock__customer_basket_query__fetch.return_value = test_case.mock__customer_basket_query__fetch__return_value

        mock__update_customer_basket_command__execute.side_effect = CQRSException
        mock__update_customer_basket_command__init.return_value = None

        try:
            add_basket_item(request_data=test_case.request_data, user_id=test_case.user_id)
        except HTTPException as e:
            assert e.status_code == test_case.expected_http_response_exception.status_code
            assert e.detail == test_case.expected_http_response_exception.detail

        call = mock__update_customer_basket_command__init.call_args_list[0]
        call_kwargs__customer_basket_arg = cast(CustomerBasketDTO, call._get_call_arguments()[1]['customer_basket'])
        expected_customer_basket_arg = (
            test_case.expected_update_customer_basket_command_init_call_args['customer_basket']
        )
        assert call_kwargs__customer_basket_arg.buyer_id == expected_customer_basket_arg.buyer_id
        self._assert(
            set(call_kwargs__customer_basket_arg.basket_items),
            set(expected_customer_basket_arg.basket_items),
        )
        mock__update_customer_basket_command__execute.assert_called_once()
