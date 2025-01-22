from typing import Dict, List, Type, Callable
from .events import DomainEvent
from .interfaces import IEventPublisher

class DomainEventPublisher(IEventPublisher):
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DomainEventPublisher, cls).__new__(cls)
            cls._instance._handlers: Dict[Type[DomainEvent], List[Callable]] = {}
        return cls._instance

    def publish(self, event: DomainEvent) -> None:
        """Publish an event to all registered handlers"""
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler(event)

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable) -> None:
        """Subscribe a handler to a specific event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def clear_handlers(self) -> None:
        """Clear all event handlers"""
        self._handlers.clear()
