"""migrate customer_basket to jsonb format

Revision ID: 9630ba02fd4f
Revises: 3d262d4f0e7a
Create Date: 2024-06-27 11:06:16.060920

"""
from collections import defaultdict
from typing import Annotated, Dict, List, Sequence, Tuple, Union

from operator import attrgetter

from alembic import op

from pydantic import BaseModel

import sqlalchemy as sa
from sqlalchemy import Connection, text
from sqlalchemy.dialects import postgresql

from basket import hints

from framework.common.dto import DTO
from framework.typing import Json

# revision identifiers, used by Alembic.
revision: str = '9630ba02fd4f'
down_revision: Union[str, None] = '3d262d4f0e7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class DBEntry(BaseModel, frozen=True):
    pass


class old_format:
    class BasketItemDBEntry(DBEntry):
        id: hints.BasketItemId
        basket_buyer_id: hints.CustomerBasketPK
        product_id: int
        product_name: str
        unit_price: float
        quantity: int
        picture_url: str

    class CustomerBasketDBEntry(DBEntry):
        buyer_id: hints.BuyerId


class new_format:
    class BasketItem(DTO):
        id: hints.BasketItemId
        product_id: int
        product_name: str
        unit_price: float
        quantity: int
        picture_url: str

    class CustomerBasketData(DTO):
        basket_items: List['new_format.BasketItem']

    class CustomerBasketDBEntry(DBEntry):
        buyer_id: hints.BuyerId

        # не явялется полем таблицы.
        # Нужно для присваения данных в формате pydantic модели, чтобы отработала pydantic валидация
        data_as_pydantic_model: 'new_format.CustomerBasketData'

        @property
        def data(self) -> Annotated[Json, 'dumps(new_format.CustomerBasketData)']:
            return self.data_as_pydantic_model.model_dump_json()


new_format.CustomerBasketDBEntry.model_rebuild()


def pull_data_from_db_and_transfer_to_new_format(connection: Connection) -> Tuple[new_format.CustomerBasketDBEntry]:
    customer_basket_rows = connection.execute(
        text("""
                SELECT buyer_id FROM basket.customer_basket
                ;
            """),
    ).fetchall()

    basket_item_rows = connection.execute(
        text(
            """
                SELECT
                    id,
                    basket_buyer_id,
                    product_id,
                    product_name,
                    unit_price,
                    quantity,
                    picture_url
                FROM basket.basket_item
                ;
            """,
        ),
    ).fetchall()

    customer_basket_entrys_in_old_format: List[old_format.CustomerBasketDBEntry] = []
    for row in customer_basket_rows:
        row_as_dict = row._asdict()
        customer_basket_entrys_in_old_format.append(old_format.CustomerBasketDBEntry(buyer_id=row_as_dict['buyer_id']))

    basket_item_entrys_in_old_format: List[old_format.BasketItemDBEntry] = []
    for row in basket_item_rows:
        row_as_dict = row._asdict()
        basket_item_entrys_in_old_format.append(
            old_format.BasketItemDBEntry(
                id=row_as_dict['id'],
                basket_buyer_id=row_as_dict['basket_buyer_id'],
                product_id=row_as_dict['product_id'],
                product_name=row_as_dict['product_name'],
                picture_url=row_as_dict['picture_url'],
                quantity=row_as_dict['quantity'],
                unit_price=row_as_dict['unit_price'],
            ),
        )

    basket_pk_to_basket_items_in_old_format: Dict[
        hints.CustomerBasketPK,
        List[old_format.BasketItemDBEntry],
    ] = defaultdict(list)
    for entry in basket_item_entrys_in_old_format:
        basket_pk_to_basket_items_in_old_format[entry.basket_buyer_id].append(entry)

    customer_basket_entrys_in_new_format: List[new_format.CustomerBasketDBEntry] = []
    for entry in customer_basket_entrys_in_old_format:
        customer_basket_entrys_in_new_format.append(
            new_format.CustomerBasketDBEntry(
                buyer_id=entry.buyer_id,
                data_as_pydantic_model=new_format.CustomerBasketData(
                    basket_items=[
                        new_format.BasketItem(
                            id=basket_item_entry.id,
                            product_id=basket_item_entry.product_id,
                            picture_url=basket_item_entry.picture_url,
                            product_name=basket_item_entry.product_name,
                            quantity=basket_item_entry.quantity,
                            unit_price=basket_item_entry.unit_price,
                        ) for basket_item_entry in basket_pk_to_basket_items_in_old_format[entry.buyer_id]
                    ],
                ),
            ),
        )

    return tuple(customer_basket_entrys_in_new_format)


def pull_data_from_db_and_transfer_to_old_format(
    connection: Connection,
) -> Tuple[
    Tuple[old_format.CustomerBasketDBEntry],
    Tuple[old_format.BasketItemDBEntry],
]:
    customer_baskets_rows = connection.execute(
        text("""
            SELECT buyer_id, data FROM basket.customer_basket;
            """),
    ).fetchall()

    customers_baskets_entrys: List[new_format.CustomerBasketDBEntry] = []
    for row in customer_baskets_rows:
        row_as_dict = row._asdict()
        customers_baskets_entrys.append(
            new_format.CustomerBasketDBEntry(
                buyer_id=row_as_dict['buyer_id'],
                data_as_pydantic_model=new_format.CustomerBasketData.model_validate(row_as_dict['data']),
            ),
        )

    customer_baskets_in_old_format: List[old_format.CustomerBasketDBEntry] = []
    basket_items_in_old_format: List[old_format.BasketItemDBEntry] = []

    for customer_basket in customers_baskets_entrys:
        customer_baskets_in_old_format.append(old_format.CustomerBasketDBEntry(buyer_id=customer_basket.buyer_id))

        for basket_item in customer_basket.data_as_pydantic_model.basket_items:
            basket_items_in_old_format.append(
                old_format.BasketItemDBEntry(
                    id=basket_item.id,
                    basket_buyer_id=customer_basket.buyer_id,
                    product_id=basket_item.product_id,
                    product_name=basket_item.product_name,
                    unit_price=basket_item.unit_price,
                    quantity=basket_item.quantity,
                    picture_url=basket_item.picture_url,
                ),
            )

    return tuple(customer_baskets_in_old_format), tuple(basket_items_in_old_format)


def upgrade() -> None:
    connection = op.get_bind()

    customer_baskets_in_new_format = pull_data_from_db_and_transfer_to_new_format(connection=connection)

    op.drop_table('basket_item', schema='basket')

    op.add_column(
        'customer_basket',
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        schema='basket',
    )

    connection.execute(text('TRUNCATE basket.customer_basket;'))

    connection.execute(
        statement=text(
            """
            INSERT INTO basket.customer_basket (buyer_id, data) VALUES (:buyer_id, :data);
            """,
        ),
        parameters=[{
            'buyer_id': entry.buyer_id,
            'data': entry.data,
        } for entry in customer_baskets_in_new_format],
    )

    op.alter_column(
        table_name='customer_basket',
        column_name='data',
        nullable=False,
        schema='basket',
    )


def downgrade() -> None:
    connection = op.get_bind()

    customer_baskets_in_old_format, basket_items_in_old_format = pull_data_from_db_and_transfer_to_old_format(
        connection=connection,
    )

    op.drop_column('customer_basket', 'data', schema='basket')

    connection.execute(text('TRUNCATE basket.customer_basket;'))

    op.create_table(
        'basket_item',
        sa.Column(
            'id',
            sa.INTEGER(),
            server_default=sa.text("nextval('basket.basket_item_id_seq'::regclass)"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column('basket_buyer_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('product_name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
        sa.Column('unit_price', sa.NUMERIC(), autoincrement=False, nullable=False),
        sa.Column('quantity', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('picture_url', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.CheckConstraint('quantity > 0', name='quantity_is_positive'),
        sa.CheckConstraint('unit_price > 0::numeric', name='unit_price_is_positive'),
        sa.ForeignKeyConstraint(
            ['basket_buyer_id'],
            ['basket.customer_basket.buyer_id'],
            name='basket_item_basket_buyer_id_fkey',
        ),
        sa.PrimaryKeyConstraint('id', name='basket_item_pkey'),
        schema='basket',
    )

    connection.execute(
        statement=text(
            """
            INSERT INTO basket.customer_basket (buyer_id) VALUES (:buyer_id);
            """,
        ),
        parameters=[{
            'buyer_id': entry.buyer_id,
        } for entry in customer_baskets_in_old_format],
    )

    connection.execute(
        statement=text(
            """
            INSERT INTO basket.basket_item (id,
                                            basket_buyer_id,
                                            product_id,
                                            product_name,
                                            unit_price,
                                            quantity,
                                            picture_url)
            VALUES (:id, :basket_buyer_id, :product_id, :product_name, :unit_price, :quantity, :picture_url);
            """,
        ),
        parameters=[
            {
                'id': entry.id,
                'basket_buyer_id': entry.basket_buyer_id,
                'product_id': entry.product_id,
                'product_name': entry.product_name,
                'unit_price': entry.unit_price,
                'quantity': entry.quantity,
                'picture_url': entry.picture_url,
            } for entry in basket_items_in_old_format
        ],
    )

    basket_item_id_seq_current_value = max(basket_items_in_old_format, key=attrgetter('id')).id
    connection.execute(
        statement=text(
            """
            SELECT setval('basket.basket_item_id_seq', :basket_item_id_seq_current_value, true);
            """,
        ),
        parameters={'basket_item_id_seq_current_value': basket_item_id_seq_current_value},
    )
