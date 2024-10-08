from typing import Annotated

import fastapi
from fastapi import Depends, Response, status

from pydantic import Field
from pydantic.types import PositiveFloat, PositiveInt

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as lib_Session

from catalog import hints
from catalog.domain.models import CatalogItem
from catalog.views.http.api_router import api_router

from catalog_cqrs_contract.event import CatalogItemPriceOrDiscountWasChangedEvent

from eshop.dependency_container import dependency_container

from framework.common.dto import DTO
from framework.cqrs.context import InsideSqlachemyTransactionContext
from framework.fastapi.dependencies.admin_required import admin_required
from framework.fastapi.http_exceptions import BadRequestException
from framework.file_storage import UploadFile
from framework.sqlalchemy.session import Session

__all__ = ('update_item', )


class CatalogItemRequestData(DTO):
    id: hints.CatalogItemId
    name: str
    description: str
    price: PositiveFloat
    catalog_type_id: hints.CatalogTypeId
    catalog_brand_id: hints.CatalogBrandId
    available_stock: PositiveInt
    restock_threshold: PositiveInt
    maxstock_threshold: PositiveInt
    on_reorder: bool
    discount: int = Field(ge=0, le=100)


class NotFoundError(Exception):
    pass


class CatalogItemData(DTO):
    price: PositiveFloat
    picture_filename: str
    discount: int = Field(ge=0, le=100)


def _fetch_catalog_item_data(catalog_item_id: hints.CatalogItemId) -> CatalogItemData:
    # yapf: disable
    stmt = select(
        CatalogItem.price,
        CatalogItem.picture_filename,
        CatalogItem.discount,
    ).where(
        CatalogItem.id == catalog_item_id,
    )
    # yapf: enable

    with Session() as session:
        with session.begin():
            result = session.execute(stmt).fetchone()

    if not result:
        raise NotFoundError('catalog item with id = %s does not exist', catalog_item_id)

    price, picture_filename, discount = result
    return CatalogItemData(
        price=price,
        picture_filename=picture_filename,
        discount=discount,
    )


def _update_catalog_item_in_db(session: lib_Session, catalog_item: CatalogItem) -> None:
    # yapf: disable
    stmt = update(
        CatalogItem,
    ).where(
        CatalogItem.id == catalog_item.id,
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


def _updated_catalog_item(
    catalog_item_request_data: CatalogItemRequestData,
    picture_filename: str,
    picture_url: str,
) -> CatalogItem:
    return CatalogItem(
        id=catalog_item_request_data.id,
        name=catalog_item_request_data.name,
        description=catalog_item_request_data.description,
        price=catalog_item_request_data.price,
        picture_filename=picture_filename,
        picture_url=picture_url,
        catalog_type_id=catalog_item_request_data.catalog_type_id,
        catalog_brand_id=catalog_item_request_data.catalog_brand_id,
        available_stock=catalog_item_request_data.available_stock,
        restock_threshold=catalog_item_request_data.restock_threshold,
        maxstock_threshold=catalog_item_request_data.maxstock_threshold,
        on_reorder=catalog_item_request_data.on_reorder,
        discount=catalog_item_request_data.discount,
    )


@api_router.put('/items/', dependencies=[Depends(admin_required)])
def update_item(
    catalog_item_request_data: Annotated[CatalogItemRequestData, Depends()],
    catalog_item_picture: fastapi.UploadFile,
) -> Response:
    try:
        catalog_item_data = _fetch_catalog_item_data(catalog_item_id=catalog_item_request_data.id)
    except NotFoundError:
        raise BadRequestException(detail=f'catalog item with id = {catalog_item_request_data.id} does not exist')

    current_catalog_item_price = catalog_item_data.price
    current_catalog_item_discount = catalog_item_data.discount
    current_catalog_item_picture_filename = catalog_item_data.picture_filename

    file_storage_api = dependency_container.file_storage_api_factory()

    picture_url = file_storage_api.url_path_for_file(filename=catalog_item_picture.filename)

    updated_catalog_item = _updated_catalog_item(
        catalog_item_request_data=catalog_item_request_data,
        picture_filename=catalog_item_picture.filename,
        picture_url=picture_url,
    )

    with Session() as session:
        with session.begin():
            try:
                _update_catalog_item_in_db(
                    session=session,
                    catalog_item=updated_catalog_item,
                )
            except IntegrityError:
                raise BadRequestException(
                    detail=f"""
                    catalog brand with id = {updated_catalog_item.catalog_brand_id}
                    or catalog type with id = {updated_catalog_item.catalog_type_id} does not exist
                    """,
                )

            is_price_changed: bool = updated_catalog_item.price != current_catalog_item_price
            is_discount_changed: bool = updated_catalog_item.discount != current_catalog_item_discount

            if is_price_changed or is_discount_changed:
                CatalogItemPriceOrDiscountWasChangedEvent(
                    catalog_item_id=updated_catalog_item.id,
                    new_price=updated_catalog_item.price,
                    new_discount=updated_catalog_item.discount,
                    context=InsideSqlachemyTransactionContext(session=session),
                ).publish()

    file_storage_api.update(
        old_file_filename=current_catalog_item_picture_filename,
        upload_file=UploadFile(file=catalog_item_picture.file, filename=catalog_item_picture.filename),
        does_not_exist_ok=False,
    )

    return Response(status_code=status.HTTP_200_OK)
