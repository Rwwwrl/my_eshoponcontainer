from __future__ import annotations

import abc
from typing import (
    Optional,
    TYPE_CHECKING,
    TypeVar,
    final,
)

from attrs import define

from ..request import BaseSyncRequest, ISyncRequest

QueryResponseType = TypeVar('QueryResponseType')

if TYPE_CHECKING:
    from ..cqrs_bus import ICQRSBus

__all__ = (
    'IQuery',
    'Query',
)


@define
class IQuery(ISyncRequest[QueryResponseType], abc.ABC):
    @abc.abstractmethod
    def fetch(self, bus: Optional[ICQRSBus] = None) -> QueryResponseType:
        raise NotImplementedError


@define
class Query(IQuery[QueryResponseType], BaseSyncRequest):
    @final
    def fetch(self, bus: Optional[ICQRSBus] = None) -> QueryResponseType:
        from ..cqrs_bus import CQRSBusSingletoneFactory

        if not bus:
            bus = CQRSBusSingletoneFactory.create()

        return bus.fetch(query=self)
