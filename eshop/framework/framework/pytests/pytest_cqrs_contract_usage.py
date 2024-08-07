import pytest

from pytest_check import check

from framework.for_pytests.for_testing_cqrs_contract_usage import ITestQueryContract, assert_attribute

from user_identity_cqrs_contract.hints import JWTToken, UserId
from user_identity_cqrs_contract.query.query import UserFromJWTTokenQuery, UserIdWithRoleDTO


@pytest.mark.cqrs_contract_usage
class TestUserIdFromJWTTokenQuery(ITestQueryContract[UserFromJWTTokenQuery]):
    def test_query_contract(self):
        with check:
            assert_attribute(UserFromJWTTokenQuery, 'jwt_token', JWTToken)

    def test_query_response_contract(self):
        response_type = UserFromJWTTokenQuery.__response_type__()

        with check:
            assert response_type == UserIdWithRoleDTO
            assert_attribute(UserIdWithRoleDTO, 'id', UserId)
