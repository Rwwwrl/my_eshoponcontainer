from typing import List, final

from basket.domain.models.customer_basket import (
    CustomerBasket,
    CustomerBasketRepository,
)

from catalog_cqrs_contract.event import CatalogItemPriceChangedEvent

from framework.cqrs.event import IEventHandler

__all__ = ('CatalogItemPriceChangedEventHandler', )


@final
@CatalogItemPriceChangedEvent.handler
class CatalogItemPriceChangedEventHandler(IEventHandler):
    def handle(self, event: CatalogItemPriceChangedEvent) -> None:
        customer_basket_repository = CustomerBasketRepository(session=event.context.session)
        customers_baskets = customer_basket_repository.all()

        updated_customers_baskets: List[CustomerBasket] = []
        for customer_basket in customers_baskets:
            for basket_item in customer_basket.data.basket_items:
                if basket_item.product_id == event.catalog_item_id:
                    basket_item.unit_price = event.new_price
                    updated_customers_baskets.append(customer_basket)

                    # в рамках одной корзины BasketItem`ы уникальны по значению `product_id`
                    break

        if updated_customers_baskets:
            for customer_basket in updated_customers_baskets:
                customer_basket_repository.save(customer_basket_orm=customer_basket)
