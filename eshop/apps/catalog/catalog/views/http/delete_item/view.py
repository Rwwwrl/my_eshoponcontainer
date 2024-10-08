from fastapi import Depends, Response, status

from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session as lib_Session

from catalog import hints
from catalog.domain.models import CatalogItem
from catalog.views.http.api_router import api_router

from catalog_cqrs_contract.event import CatalogItemHasBeenDeletedEvent

from eshop.dependency_container import dependency_container

from framework.cqrs.context import InsideSqlachemyTransactionContext
from framework.fastapi.dependencies.admin_required import admin_required
from framework.sqlalchemy.session import Session

__all__ = ('delete_item', )


def _check_if_catalog_item_exists(session: lib_Session, catalog_item_id: hints.CatalogItemId) -> bool:
    stmt = text('SELECT EXISTS(SELECT 1 from catalog.catalog_item WHERE id = :id);')
    return session.scalar(stmt, params={'id': catalog_item_id})


def _delete_catalog_item_from_db(session: lib_Session, catalog_item_id: hints.CatalogItemId) -> None:
    stmt = delete(CatalogItem).where(CatalogItem.id == catalog_item_id)
    session.execute(stmt)


def _fetch_catalog_item_picture_url(session: lib_Session, catalog_item_id: hints.CatalogItemId) -> str:
    stmt = select(CatalogItem.picture_url).where(CatalogItem.id == catalog_item_id)
    return session.scalar(stmt)


@api_router.delete('/items/', dependencies=[Depends(admin_required)])
def delete_item(catalog_item_id: hints.CatalogItemId) -> Response:
    with Session() as session:
        with session.begin():
            is_catalog_item_exists = _check_if_catalog_item_exists(
                session=session,
                catalog_item_id=catalog_item_id,
            )

    if is_catalog_item_exists:
        with Session() as session, session.begin():
            catalog_item_picture_url = _fetch_catalog_item_picture_url(
                session=session,
                catalog_item_id=catalog_item_id,
            )

        with Session() as session, session.begin():
            event = CatalogItemHasBeenDeletedEvent(
                catalog_item_id=catalog_item_id,
                context=InsideSqlachemyTransactionContext(session=session),
            )
            _delete_catalog_item_from_db(session=session, catalog_item_id=catalog_item_id)
            event.publish()

        dependency_container.file_storage_api_factory().delete(url_path_to_file=catalog_item_picture_url)

    return Response(status_code=status.HTTP_200_OK)
