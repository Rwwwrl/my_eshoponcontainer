from framework.for_pytests.for_testing_cqrs_contract_usage import ITestQueryContract, assert_attribute

from user_identity_cqrs_contract.query import UserFromJWTTokenQuery
from user_identity_cqrs_contract.query.query_response import UserIdWithRoleDTO, UserRoleEnum


class TestUserIdFromJWTTokenQuery(ITestQueryContract[UserFromJWTTokenQuery]):
    def test_query_contract(self):
        assert_attribute(UserFromJWTTokenQuery, 'jwt_token', str)

    def test_query_response_contract(self):
        response_type = UserFromJWTTokenQuery.__response_type__()

        assert response_type == UserIdWithRoleDTO
        assert_attribute(UserIdWithRoleDTO, 'id', int)
        assert_attribute(UserIdWithRoleDTO, 'role', UserRoleEnum)
