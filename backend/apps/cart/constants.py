"""Cart-related constants."""

# Cart event types
CART_EVENT_CREATED = 'cart_created'
CART_EVENT_CHECKOUT_STARTED = 'checkout_started'
CART_EVENT_CLEARED = 'cleared'
CART_EVENT_ITEM_ADDED = 'item_added'
CART_EVENT_ITEM_REMOVED = 'item_removed'
CART_EVENT_QUANTITY_UPDATED = 'quantity_updated'
CART_EVENT_STOCK_UPDATED = 'stock_updated'
CART_EVENT_EXPIRED = 'expired'
CART_EVENT_MERGED = 'merged'
CART_EVENT_BATCH_ADD = 'batch_add'
CART_EVENT_BATCH_UPDATE = 'batch_update'

CART_EVENT_TYPES = (
    (CART_EVENT_CREATED, 'Cart created'),
    (CART_EVENT_CHECKOUT_STARTED, 'Checkout started'),
    (CART_EVENT_CLEARED, 'Cart cleared'),
    (CART_EVENT_ITEM_ADDED, 'Item added'),
    (CART_EVENT_ITEM_REMOVED, 'Item removed'),
    (CART_EVENT_QUANTITY_UPDATED, 'Quantity updated'),
    (CART_EVENT_STOCK_UPDATED, 'Stock updated'),
    (CART_EVENT_EXPIRED, 'Cart expired'),
    (CART_EVENT_MERGED, 'Cart merged'),
    (CART_EVENT_BATCH_ADD, 'Batch items added'),
    (CART_EVENT_BATCH_UPDATE, 'Batch quantities updated')
)
