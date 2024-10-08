from typing import Annotated

import fastapi
from fastapi import Depends, Response, status

from pydantic import Field
from pydantic.types import PositiveFloat, PositiveInt

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as lib_Session

from catalog import hints
from catalog.domain.models import CatalogItem
from catalog.views.http.api_router import api_router

from eshop.dependency_container import dependency_container

from framework.common.dto import DTO
from framework.fastapi.dependencies.admin_required import admin_required
from framework.fastapi.http_exceptions import BadRequestException
from framework.file_storage import UploadFile
from framework.sqlalchemy.session import Session

__all__ = ('create_item', )


class NewCatalogItemRequestData(DTO):
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


def _save_new_catalog_item_to_db(session: lib_Session, new_catalog_item: CatalogItem) -> None:
    session.add(new_catalog_item)


def _new_catalog_item(
    new_catalog_item_request_data: NewCatalogItemRequestData,
    picture_filename: str,
    picture_url: str,
) -> CatalogItem:
    return CatalogItem(
        name=new_catalog_item_request_data.name,
        description=new_catalog_item_request_data.description,
        price=new_catalog_item_request_data.price,
        picture_filename=picture_filename,
        picture_url=picture_url,
        catalog_type_id=new_catalog_item_request_data.catalog_type_id,
        catalog_brand_id=new_catalog_item_request_data.catalog_brand_id,
        available_stock=new_catalog_item_request_data.available_stock,
        restock_threshold=new_catalog_item_request_data.restock_threshold,
        maxstock_threshold=new_catalog_item_request_data.maxstock_threshold,
        on_reorder=new_catalog_item_request_data.on_reorder,
        discount=new_catalog_item_request_data.discount,
    )


@api_router.post('/items/', dependencies=[Depends(admin_required)])
def create_item(
    new_catalog_item_request_data: Annotated[NewCatalogItemRequestData, Depends()],
    catalog_item_picture: fastapi.UploadFile,
) -> Response:
    file_storage_api = dependency_container.file_storage_api_factory()

    picture_url = file_storage_api.url_path_for_file(filename=catalog_item_picture.filename)

    new_catalog_item = _new_catalog_item(
        new_catalog_item_request_data=new_catalog_item_request_data,
        picture_filename=catalog_item_picture.filename,
        picture_url=picture_url,
    )

    with Session() as session:
        try:
            with session.begin():
                _save_new_catalog_item_to_db(session=session, new_catalog_item=new_catalog_item)
        except IntegrityError:
            raise BadRequestException(
                detail=f"""
                catalog brand with id = {new_catalog_item.catalog_brand_id}
                or catalog type with id = {new_catalog_item.catalog_type_id} does not exist
                """,
            )

    file_storage_api.upload(
        upload_file=UploadFile(
            file=catalog_item_picture.file,
            filename=catalog_item_picture.filename,
        ),
    )

    return Response(status_code=status.HTTP_201_CREATED)
