from fastapi import Response, status

from pydantic.types import PositiveFloat, PositiveInt

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as lib_Session

from catalog import hints
from catalog.api_router import api_router
from catalog.infrastructure.persistance.postgres.models import CatalogItemORM

from catalog_cqrs_contract.event import CatalogItemPriceChangedEvent

from framework.common.dto import DTO
from framework.fastapi.http_exceptions import BadRequestException
from framework.sqlalchemy.session import Session

__all__ = ('update_item', )


class CatalogItemRequestData(DTO):
    id: hints.CatalogItemId
    name: str
    description: str
    price: PositiveFloat

    # TODO пока что это будет передавать именно так, а не ввиде файла
    picture_filename: str
    picture_url: str

    catalog_type_id: hints.CatalogTypeId
    catalog_brand_id: hints.CatalogBrandId
    available_stock: PositiveInt
    restock_threshold: PositiveInt
    maxstock_threshold: PositiveInt
    on_reorder: bool


class NotFoundError(Exception):
    pass


def _fetch_current_catalog_item_price(catalog_item_id: hints.CatalogItemId) -> PositiveFloat:
    stmt = select(CatalogItemORM.price).where(CatalogItemORM.id == catalog_item_id)

    with Session() as session:
        with session.begin():
            price = session.scalar(stmt)

    if not price:
        raise NotFoundError('catalog item with id = %s does not exist', catalog_item_id)

    return price


def _update_catalog_item_in_db(session: lib_Session, catalog_item: CatalogItemORM) -> None:
    # yapf: disable
    stmt = update(
        CatalogItemORM,
    ).where(
        CatalogItemORM.id == catalog_item.id,
    ).values(
        name=catalog_item.name,
        description=catalog_item.description,
        price=catalog_item.price,
        picture_filename=catalog_item.picture_filename,
        picture_url=catalog_item.picture_url,
        catalog_type_id=catalog_item.catalog_type_id,
        catalog_brand_id=catalog_item.catalog_brand_id,
        available_stock=catalog_item.available_stock,
        restock_threshold=catalog_item.restock_threshold,
        maxstock_threshold=catalog_item.maxstock_threshold,
        on_reorder=catalog_item.on_reorder,
    )
    # yapf: enable

    session.execute(stmt)


def _updated_catalog_item(catalog_item_request_data: CatalogItemRequestData) -> CatalogItemORM:
    return CatalogItemORM(
        id=catalog_item_request_data.id,
        name=catalog_item_request_data.name,
        description=catalog_item_request_data.description,
        price=catalog_item_request_data.price,
        picture_filename=catalog_item_request_data.picture_filename,
        picture_url=catalog_item_request_data.picture_url,
        catalog_type_id=catalog_item_request_data.catalog_type_id,
        catalog_brand_id=catalog_item_request_data.catalog_brand_id,
        available_stock=catalog_item_request_data.available_stock,
        restock_threshold=catalog_item_request_data.restock_threshold,
        maxstock_threshold=catalog_item_request_data.maxstock_threshold,
        on_reorder=catalog_item_request_data.on_reorder,
    )


# TODO: доступ к эндпоинту должен иметь только админ
@api_router.put('/items/')
def update_item(catalog_item_request_data: CatalogItemRequestData) -> Response:
    try:
        current_catalog_item_price = _fetch_current_catalog_item_price(catalog_item_id=catalog_item_request_data.id)
    except NotFoundError:
        raise BadRequestException(detail=f'catalog item with id = {catalog_item_request_data.id} does not exist')

    updated_catalog_item = _updated_catalog_item(catalog_item_request_data=catalog_item_request_data)

    with Session() as session:
        with session.begin():
            try:
                _update_catalog_item_in_db(
                    session=session,
                    catalog_item=updated_catalog_item,
                )
            except IntegrityError:
                raise BadRequestException(
                    detail=f'''
                    catalog brand with id = {updated_catalog_item.catalog_brand_id}
                    or catalog type with id = {updated_catalog_item.catalog_type_id} does not exist
                    ''',
                )

            if current_catalog_item_price != catalog_item_request_data.price:
                # TODO: реализовать обработчик
                CatalogItemPriceChangedEvent(
                    catalog_item_id=updated_catalog_item.id,
                    old_price=current_catalog_item_price,
                    new_price=updated_catalog_item.price,
                ).publish()

    return Response(status_code=status.HTTP_200_OK)