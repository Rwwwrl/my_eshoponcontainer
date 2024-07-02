from typing import List, cast

from fastapi import HTTPException, status

from mock import Mock, patch

import pytest

from typing_extensions import TypedDict

from api_gateway.mediator.views.http.basket.api_router import api_router
from api_gateway.mediator.views.http.basket.update_basket import update_basket
from api_gateway.mediator.views.http.basket.update_basket.dto import (
    UpdateBasketRequestData,
    UpdateBasketRequestItemData,
)

from basket_cqrs_contract.command import UpdateCustomerBasketCommand
from basket_cqrs_contract.customer_basket_dto import BasketItemDTO, CustomerBasketDTO

from catalog_cqrs_contract.query.query import CatalogItemsByIdsQuery
from catalog_cqrs_contract.query.query_response import CatalogBrandDTO, CatalogItemDTO, CatalogTypeDTO

from framework.cqrs.exceptions import CQRSException
from framework.for_pytests.for_testing_http_views import ExpectedHttpResponse, ExpectedHttpResponseException
from framework.for_pytests.test_case import TestCase
from framework.for_pytests.test_class import TestClass


class ExpectedUpdateCustomerBasketCommandInitCallArgs(TypedDict):
    customer_basket: CustomerBasketDTO


class TestCaseSuccess(TestCase):
    request_data: UpdateBasketRequestData
    mock__catalog_item_by_ids_query__fetch__return_value: List[CatalogItemDTO]
    expected_update_customerer_basket_command_init_call_args: ExpectedUpdateCustomerBasketCommandInitCallArgs
    expected_http_response: ExpectedHttpResponse


class TestCase400BasketMustHaveAtLeastOneBasketItem(TestCase):
    request_data: UpdateBasketRequestData
    expected_http_response_exception: ExpectedHttpResponseException


class TestCase400BasketReferToNonExistingProducts(TestCase):
    request_data: UpdateBasketRequestData
    mock__catalog_item_by_ids_query__fetch__return_value: List[CatalogItemDTO]
    expected_http_response_exception: ExpectedHttpResponseException


class TestCase500FailedToUpdateBasketDueToUpdateCustomerBasketCommandFailed(TestCase):
    request_data: UpdateBasketRequestData
    mock__catalog_item_by_ids_query__fetch__return_value: List[CatalogItemDTO]
    expected_update_customerer_basket_command_init_call_args: ExpectedUpdateCustomerBasketCommandInitCallArgs
    expected_http_response_exception: ExpectedHttpResponseException


@pytest.fixture(scope='session')
def test_case_success() -> TestCaseSuccess:
    request_data = UpdateBasketRequestData(
        buyer_id=1,
        basket_items=[
            UpdateBasketRequestItemData(
                product_id=1,
                quantity=1,
            ),
            UpdateBasketRequestItemData(
                product_id=2,
                quantity=2,
            ),
        ],
    )

    mock__catalog_item_by_ids_query__fetch__return_value: List[CatalogItemDTO] = [
        CatalogItemDTO(
            id=1,
            name='name1',
            description='description1',
            price=100,
            picture_filename='picture_filename1',
            picture_url='picture_url1',
            catalog_type=CatalogTypeDTO(
                id=1,
                type='type1',
            ),
            catalog_brand=CatalogBrandDTO(
                id=1,
                brand='brand1',
            ),
            available_stock=10,
            restock_threshold=5,
            maxstock_threshold=15,
            on_reorder=False,
        ),
        CatalogItemDTO(
            id=2,
            name='name2',
            description='description2',
            price=200,
            picture_filename='picture_filename2',
            picture_url='picture_url2',
            catalog_type=CatalogTypeDTO(
                id=1,
                type='type1',
            ),
            catalog_brand=CatalogBrandDTO(
                id=1,
                brand='brand1',
            ),
            available_stock=10,
            restock_threshold=5,
            maxstock_threshold=15,
            on_reorder=False,
        ),
    ]

    expected_update_customerer_basket_command_init_call_args: ExpectedUpdateCustomerBasketCommandInitCallArgs = {
        'customer_basket':
            CustomerBasketDTO(
                buyer_id=1,
                basket_items=[
                    [
                        BasketItemDTO(
                            id=None,
                            product_id=1,
                            product_name='name1',
                            unit_price=100,
                            quantity=1,
                            picture_url='picture_url1',
                        ),
                        BasketItemDTO(
                            id=None,
                            product_id=2,
                            product_name='name2',
                            unit_price=200,
                            quantity=2,
                            picture_url='picture_url2',
                        ),
                    ],
                ],
            ),
    }

    return TestCaseSuccess(
        request_data=request_data,
        mock__catalog_item_by_ids_query__fetch__return_value=mock__catalog_item_by_ids_query__fetch__return_value,
        expected_update_customerer_basket_command_init_call_args=(
            expected_update_customerer_basket_command_init_call_args
        ),
        expected_http_response=ExpectedHttpResponse(status_code=status.HTTP_200_OK, body=b''),
    )


@pytest.fixture(scope='session')
def test_case_400_basket_must_have_at_least_one_basket_item() -> TestCase400BasketMustHaveAtLeastOneBasketItem:
    request_data = UpdateBasketRequestData(
        buyer_id=1,
        basket_items=[],
    )

    return TestCase400BasketMustHaveAtLeastOneBasketItem(
        request_data=request_data,
        expected_http_response_exception=ExpectedHttpResponseException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='basket must have at least one basket item',
        ),
    )


@pytest.fixture(scope='session')
def test_case_400_basket_refer_to_non_existing_products() -> TestCase400BasketReferToNonExistingProducts:
    request_data = UpdateBasketRequestData(
        buyer_id=1,
        basket_items=[
            UpdateBasketRequestItemData(
                product_id=10,
                quantity=1,
            ),
            UpdateBasketRequestItemData(
                product_id=20,
                quantity=2,
            ),
        ],
    )

    mock__catalog_item_by_ids_query__fetch__return_value: List[CatalogItemDTO] = [
        CatalogItemDTO(
            id=1,
            name='name1',
            description='description1',
            price=100,
            picture_filename='picture_filename1',
            picture_url='picture_url1',
            catalog_type=CatalogTypeDTO(
                id=1,
                type='type1',
            ),
            catalog_brand=CatalogBrandDTO(
                id=1,
                brand='brand1',
            ),
            available_stock=10,
            restock_threshold=5,
            maxstock_threshold=15,
            on_reorder=False,
        ),
        CatalogItemDTO(
            id=2,
            name='name2',
            description='description2',
            price=200,
            picture_filename='picture_filename2',
            picture_url='picture_url2',
            catalog_type=CatalogTypeDTO(
                id=1,
                type='type1',
            ),
            catalog_brand=CatalogBrandDTO(
                id=1,
                brand='brand1',
            ),
            available_stock=10,
            restock_threshold=5,
            maxstock_threshold=15,
            on_reorder=False,
        ),
    ]

    return TestCase400BasketReferToNonExistingProducts(
        request_data=request_data,
        mock__catalog_item_by_ids_query__fetch__return_value=mock__catalog_item_by_ids_query__fetch__return_value,
        expected_http_response_exception=ExpectedHttpResponseException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='basket refer to non-existing products, invalid products: [10, 20]',
        ),
    )


@pytest.fixture(scope='session')
def test_case_500_failed_to_update_basket_due_to_UpdateCustomerBasketCommand_failed(
) -> TestCase500FailedToUpdateBasketDueToUpdateCustomerBasketCommandFailed:
    request_data = UpdateBasketRequestData(
        buyer_id=1,
        basket_items=[
            UpdateBasketRequestItemData(
                product_id=1,
                quantity=1,
            ),
            UpdateBasketRequestItemData(
                product_id=2,
                quantity=2,
            ),
        ],
    )

    mock__catalog_item_by_ids_query__fetch__return_value: List[CatalogItemDTO] = [
        CatalogItemDTO(
            id=1,
            name='name1',
            description='description1',
            price=100,
            picture_filename='picture_filename1',
            picture_url='picture_url1',
            catalog_type=CatalogTypeDTO(
                id=1,
                type='type1',
            ),
            catalog_brand=CatalogBrandDTO(
                id=1,
                brand='brand1',
            ),
            available_stock=10,
            restock_threshold=5,
            maxstock_threshold=15,
            on_reorder=False,
        ),
        CatalogItemDTO(
            id=2,
            name='name2',
            description='description2',
            price=200,
            picture_filename='picture_filename2',
            picture_url='picture_url2',
            catalog_type=CatalogTypeDTO(
                id=1,
                type='type1',
            ),
            catalog_brand=CatalogBrandDTO(
                id=1,
                brand='brand1',
            ),
            available_stock=10,
            restock_threshold=5,
            maxstock_threshold=15,
            on_reorder=False,
        ),
    ]

    expected_update_customerer_basket_command_init_call_args: ExpectedUpdateCustomerBasketCommandInitCallArgs = {
        'customer_data':
            CustomerBasketDTO(
                buyer_id=1,
                basket_items=[
                    BasketItemDTO(
                        product_id=1,
                        product_name='name1',
                        unit_price=100,
                        quantity=1,
                        picture_url='picture_url1',
                    ),
                    BasketItemDTO(
                        product_id=2,
                        product_name='name2',
                        unit_price=200,
                        quantity=2,
                        picture_url='picture_url2',
                    ),
                ],
            ),
    }

    return TestCase500FailedToUpdateBasketDueToUpdateCustomerBasketCommandFailed(
        request_data=request_data,
        mock__catalog_item_by_ids_query__fetch__return_value=mock__catalog_item_by_ids_query__fetch__return_value,
        expected_update_customerer_basket_command_init_call_args=(
            expected_update_customerer_basket_command_init_call_args
        ),
        expected_http_response_exception=ExpectedHttpResponseException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'failed to update basket due to {UpdateCustomerBasketCommand.__name__} failed',
        ),
    )


class TestUrlToView(TestClass[update_basket]):
    def test(self):
        expected_url = '/api_gateway/basket/basket/'
        fact_url = api_router.url_path_for(update_basket.__name__)
        assert fact_url == expected_url


class TestViewUpdateBasket(TestClass[update_basket]):
    @patch.object(UpdateCustomerBasketCommand, 'execute')
    @patch.object(UpdateCustomerBasketCommand, '__init__')
    @patch.object(CatalogItemsByIdsQuery, 'fetch')
    def test_case_success(
        self,
        mock__catalog_item_by_ids_query__fetch: Mock,
        mock__update_customer_basket_command__init: Mock,
        mock__update_customer_basket_command__execute: Mock,
        test_case_success: TestCaseSuccess,
    ):
        test_case = test_case_success

        mock__update_customer_basket_command__init.return_value = None
        mock__catalog_item_by_ids_query__fetch.return_value = (
            test_case.mock__catalog_item_by_ids_query__fetch__return_value
        )

        response = update_basket(request_data=test_case.request_data, user_id=1)
        assert response.status_code == test_case.expected_http_response.status_code
        assert response.body == test_case.expected_http_response.body

        call = mock__update_customer_basket_command__init.call_args_list[0]
        call_kwargs__customer_basket_arg = cast(CustomerBasketDTO, call._get_call_arguments()[1]['customer_basket'])
        expected_customer_basket_arg = (
            test_case.expected_update_customerer_basket_command_init_call_args['customer_basket']
        )
        assert call_kwargs__customer_basket_arg.buyer_id == expected_customer_basket_arg.buyer_id
        self._assert(
            set(call_kwargs__customer_basket_arg.basket_items),
            set(expected_customer_basket_arg.basket_items),
        )
        mock__update_customer_basket_command__execute.assert_called_once()

    def test_case_400_basket_must_have_at_least_one_basket_item(
        self,
        test_case_400_basket_must_have_at_least_one_basket_item: TestCase400BasketMustHaveAtLeastOneBasketItem,
    ):
        test_case = test_case_400_basket_must_have_at_least_one_basket_item

        try:
            update_basket(request_data=test_case.request_data, user_id=1)
        except HTTPException as e:
            assert e.status_code == test_case.expected_http_response_exception.status_code
            assert e.detail == test_case.expected_http_response_exception.detail

    @patch.object(CatalogItemsByIdsQuery, 'fetch')
    def test_case_400_basket_refer_to_non_existing_products(
        self,
        mock__catalog_item_by_ids_query__fetch: Mock,
        test_case_400_basket_refer_to_non_existing_products: TestCase400BasketReferToNonExistingProducts,
    ):
        test_case = test_case_400_basket_refer_to_non_existing_products

        mock__catalog_item_by_ids_query__fetch.return_value = (
            test_case.mock__catalog_item_by_ids_query__fetch__return_value
        )

        try:
            update_basket(request_data=test_case.request_data, user_id=1)
        except HTTPException as e:
            assert e.status_code == test_case.expected_http_response_exception.status_code
            assert e.detail == test_case.expected_http_response_exception.detail

    @patch.object(UpdateCustomerBasketCommand, 'execute')
    @patch.object(UpdateCustomerBasketCommand, '__init__')
    @patch.object(CatalogItemsByIdsQuery, 'fetch')
    def test_case_500_failed_to_update_basket_due_to_UpdateCustomerBasketCommand_failed(
        self,
        mock__catalog_item_by_ids_query__fetch: Mock,
        mock__update_customer_basket_command__init: Mock,
        mock__update_customer_basket_command__execute: Mock,
        test_case_500_failed_to_update_basket_due_to_UpdateCustomerBasketCommand_failed:
        TestCase500FailedToUpdateBasketDueToUpdateCustomerBasketCommandFailed,
    ):
        test_case = test_case_500_failed_to_update_basket_due_to_UpdateCustomerBasketCommand_failed

        mock__update_customer_basket_command__init.return_value = None
        mock__catalog_item_by_ids_query__fetch.return_value = (
            test_case.mock__catalog_item_by_ids_query__fetch__return_value
        )

        mock__update_customer_basket_command__execute.side_effect = CQRSException

        try:
            update_basket(request_data=test_case.request_data, user_id=1)
        except HTTPException as e:
            assert e.status_code == test_case.expected_http_response_exception.status_code
            assert e.detail == test_case.expected_http_response_exception.detail

        call = mock__update_customer_basket_command__init.call_args_list[0]
        call_kwargs__customer_basket_arg = cast(CustomerBasketDTO, call._get_call_arguments()[1]['customer_basket'])
        expected_customer_basket_arg = (
            test_case.expected_update_customerer_basket_command_init_call_args['customer_basket']
        )
        assert call_kwargs__customer_basket_arg.buyer_id == expected_customer_basket_arg.buyer_id
        self._assert(
            set(call_kwargs__customer_basket_arg.basket_items),
            set(expected_customer_basket_arg.basket_items),
        )
        mock__update_customer_basket_command__execute.assert_called_once()
