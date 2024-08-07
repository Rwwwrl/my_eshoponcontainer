from __future__ import annotations

import abc
from typing import (
    Optional,
    TYPE_CHECKING,
    final,
)

from ..request import BaseAsyncRequest, IAsyncRequest

if TYPE_CHECKING:
    from ..cqrs_bus import ICQRSBus

__all__ = (
    'IAsyncCommand',
    'AsyncCommand',
)


class IAsyncCommand(IAsyncRequest, abc.ABC):
    @abc.abstractmethod
    def execute(self, bus: Optional[ICQRSBus] = None) -> None:
        raise NotImplementedError


class AsyncCommand(IAsyncCommand, BaseAsyncRequest):
    @final
    def execute(self, bus: Optional[ICQRSBus] = None) -> None:
        from ..cqrs_bus import CQRSBusSingletoneFactory

        if not bus:
            bus = CQRSBusSingletoneFactory.create()

        bus.async_execute(command=self)
