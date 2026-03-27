"""Message bus module for decoupled channel-agent communication."""

from TARS.bus.events import InboundMessage, OutboundMessage
from TARS.bus.queue import MessageBus

__all__ = ["MessageBus", "InboundMessage", "OutboundMessage"]
