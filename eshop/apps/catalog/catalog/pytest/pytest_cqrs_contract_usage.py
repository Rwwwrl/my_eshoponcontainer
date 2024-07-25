from catalog_cqrs_contract import hints
from catalog_cqrs_contract.event import CatalogItemPriceChangedEvent

from framework.for_pytests.for_testing_cqrs_contract_usage import ITestEventContract, assert_attribute


class TestCatalogItemPriceChangedEvent(ITestEventContract[CatalogItemPriceChangedEvent]):
    def test_event_contract(self) -> None:
        assert_attribute(CatalogItemPriceChangedEvent, 'catalog_item_id', hints.CatalogItemId)
        assert_attribute(CatalogItemPriceChangedEvent, 'old_price', float)
        assert_attribute(CatalogItemPriceChangedEvent, 'new_price', float)