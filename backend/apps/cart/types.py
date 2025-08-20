"""Type definitions for cart module."""
from typing import TypeVar, Dict, Any, List, Tuple, Optional, Union
from decimal import Decimal
import uuid

# Type variables
CartType = TypeVar('CartType', bound='Cart')
CartItemType = TypeVar('CartItemType', bound='CartItem')
CartEventType = TypeVar('CartEventType', bound='CartEvent')

# Common type aliases
ProductId = uuid.UUID
Quantity = int
Price = Decimal
JsonDict = Dict[str, Any]

# Complex types
CartItemData = Tuple[ProductId, Quantity]
CartItemList = List[CartItemData]
CartUpdateData = Dict[ProductId, Quantity]
