from basket.infrastructure.persistence.postgres.customer_basket.customer_basket_orm import (
    BasketItem,
    CustomerBasketORM,
    Data,
)

from framework.sqlalchemy.session_factory import session_factory


def create_customer_basket():
    with session_factory() as session:
        customer_basket1 = CustomerBasketORM(
            buyer_id=1,
            data=Data(
                basket_items=[
                    BasketItem(
                        id=1,
                        product_id=1,
                        product_name='name1',
                        unit_price=10,
                        quantity=1,
                        picture_url='root/filename1',
                    ),
                    BasketItem(
                        id=2,
                        product_id=2,
                        product_name='name2',
                        unit_price=20,
                        quantity=2,
                        picture_url='root/filename2',
                    ),
                ],
            ),
        )

        session.add(customer_basket1)
        session.commit()


if __name__ == '__main__':
    create_customer_basket()
