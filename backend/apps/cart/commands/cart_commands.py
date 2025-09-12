"""Cart command implementations."""
from typing import Optional
from django.core.exceptions import ValidationError
from django.db import transaction, DatabaseError, OperationalError, IntegrityError
from django.utils import timezone
from apps.cart.exceptions import VersionConflict
from apps.core.exceptions import VersionConflictError
from .base import BaseCommand
from ..models import Cart, CartItem, CartEvent
from ..strategies.base import CartOperationStrategy
from ..strategies.quantity_strategies import AddQuantityStrategy, RemoveQuantityStrategy, UpdateQuantityStrategy
from ..strategies.cart_strategies import ExpireCartStrategy, MergeCartStrategy
from ..services.cart_event_service import CartEventService
from apps.products.models import Product
from ..exceptions import InsufficientStockError, CartError
import logging
from apps.cart.utils.version_control import (
    CartVersionService,
    CartItemVersionService,
    CartItemLock,
    with_cart_lock
)
from django.http import HttpRequest

logger = logging.getLogger(__name__)

class AddItemCommand(BaseCommand[CartItem]):
    """Command for adding items to cart."""
    
    def __init__(self, cart: Cart, product: Product, quantity: int):
        strategy = AddQuantityStrategy(cart)
        super().__init__(cart, strategy)
        self.product = product
        self.quantity = quantity
        self.cart_item = None
        self._event_service = CartEventService()
        
    def _execute(self) -> CartItem:
        """Execute add item command."""
        try:
            with transaction.atomic():
                # Lock product for update and validate stock
                try:
                    product = Product.objects.select_for_update(nowait=True).get(pk=self.product.pk)
                except OperationalError:
                    # If we can't get the lock, raise a version conflict
                    raise VersionConflict(obj_type="Cart", obj_id=self.cart.pk)
                    
                if self.quantity > product.stock:
                    raise InsufficientStockError(
                        f"Insufficient stock. Requested: {self.quantity}, Available: {product.stock}"
                    )
                
                # Get or create cart item
                try:
                    cart_item = CartItem.objects.select_for_update(nowait=True).filter(
                        cart=self.cart,
                        product=self.product
                    ).first()
                except OperationalError:
                    # If we can't get the lock, raise a version conflict
                    raise VersionConflict(obj_type="Cart", obj_id=self.cart.pk)
                
                if cart_item:
                    new_quantity = cart_item.quantity + self.quantity
                    # Check if total quantity exceeds stock
                    if new_quantity > product.stock:
                        raise InsufficientStockError(
                            f"Insufficient stock. Total requested: {new_quantity}, Available: {product.stock}"
                        )
                    cart_item.quantity = new_quantity
                    cart_item.unit_price = product.price
                    cart_item.save()
                else:
                    cart_item = CartItem.objects.create(
                        cart=self.cart,
                        product=self.product,
                        quantity=self.quantity,
                        unit_price=product.price
                    )
                
                # Update product stock
                product.stock -= self.quantity
                product.save(update_fields=['stock'])

                # Log event
                self._event_service.log_event(
                    cart=self.cart,
                    event_type=CartEvent.ITEM_ADDED,
                    product=self.product,
                    quantity=self.quantity,
                    details={
                        'old_stock': product.stock + self.quantity,
                        'new_stock': product.stock,
                        'operation': 'add_item'
                    }
                )
                
                return cart_item
                
        except InsufficientStockError:
            raise
        except (VersionConflictError, VersionConflict):
            raise
        except Exception as e:
            logger.error(f"Error executing add item command: {str(e)}")
            raise VersionConflict(obj_type="Cart", obj_id=self.cart.pk)

class UpdateItemCommand(BaseCommand[Optional[CartItem]]):
    """Command for updating cart item quantities."""
    
    def __init__(self, cart: Cart, product: Product, quantity: int):
        strategy = UpdateQuantityStrategy(cart)
        super().__init__(cart, strategy)
        self.product = product
        self.quantity = quantity
        self._old_quantity = None
        self._event_service = CartEventService()
        
    def _execute(self) -> Optional[CartItem]:
        """Execute update quantity command."""
        cart_item = self.cart.items.filter(product=self.product).first()
        if not cart_item:
            raise ValidationError(f"Product {self.product.name} not found in cart")
            
        self._old_quantity = cart_item.quantity
        updated_item = self.strategy.execute(cart_item, self.quantity)
        
        # Log event
        self._event_service.log_event(
            cart=self.cart,
            event_type=CartEvent.QUANTITY_UPDATED,
            product=self.product,
            quantity=self.quantity
        )
        
        return updated_item

    def undo(self) -> None:
        """Undo update item command."""
        if self._old_quantity is not None:
            cart_item = self.cart.items.filter(product=self.product).first()
            if cart_item:
                cart_item.quantity = self._old_quantity
                cart_item.save()

class RemoveItemCommand(BaseCommand[None]):
    """Command for removing items from cart."""
    
    def __init__(self, cart: Cart, product: Product):
        strategy = RemoveQuantityStrategy(cart)
        super().__init__(cart, strategy)
        self.product = product
        self._removed_item = None
        self._event_service = CartEventService()
        
    def _execute(self) -> None:
        """Execute remove item command."""
        cart_item = self.cart.items.filter(product=self.product).first()
        if cart_item:
            self._removed_item = cart_item
            self.strategy.execute(cart_item, 0)
            
            # Log event
            self._event_service.log_event(
                cart=self.cart,
                event_type=CartEvent.ITEM_REMOVED,
                product=self.product
            )
            
    def undo(self) -> None:
        """Undo remove item command."""
        if self._removed_item:
            self._removed_item.pk = None
            self._removed_item.save()

class ClearCartCommand(BaseCommand[None]):
    """Command for clearing all items from cart."""
    
    def __init__(self, cart: Cart):
        strategy = RemoveQuantityStrategy(cart)
        super().__init__(cart, strategy)
        self._removed_items = []
        self._event_service = CartEventService()
        
    def _execute(self) -> None:
        """Execute clear cart command."""
        items = self.cart.items.select_related('product').all()
        self._removed_items = list(items)
        
        for item in items:
            self.strategy.execute(item, 0)
            
        # Log event
        self._event_service.log_event(
            cart=self.cart,
            event_type=CartEvent.CLEARED
        )
            
    def undo(self) -> None:
        """Undo clear cart command."""
        for item in self._removed_items:
            item.pk = None
            item.save()

class ExpireCartCommand(BaseCommand[bool]):
    """Command for marking cart as expired."""
    
    def __init__(self, cart: Cart):
        strategy = ExpireCartStrategy(cart)
        super().__init__(cart, strategy)
        
    def _execute(self) -> bool:
        """Execute expire cart command."""
        return self.strategy.execute(self.cart)

class ValidateCartCommand:
    """Command to validate cart state."""
    
    def __init__(self, cart: Cart):
        """Initialize with cart to validate."""
        self.cart = cart
        
    def execute(self) -> Optional[Cart]:
        """Execute validation."""
        if not self.cart:
            return None
            
        try:
            # Check if cart is completed or expired
            if self.cart.completed or self.cart.is_expired():
                return None
                
            # Refresh cart to get latest state
            self.cart.refresh_from_db()
            
            # Validate cart version
            if not self.cart.version:
                self.cart.version = 1
                self.cart.save()
                
            return self.cart
        except (VersionConflictError, VersionConflict):
            # Log but return cart since this is just validation
            logger.warning(f"Version conflict validating cart {self.cart.id}")
            return self.cart
        except Exception as e:
            logger.error(f"Error validating cart: {str(e)}")
            return None

class RetrieveCartCommand(BaseCommand[Optional[Cart]]):
    """Command for retrieving or creating cart."""
    
    def __init__(self, request: HttpRequest):
        super().__init__(None, None)
        self.request = request
        
    def _execute(self) -> Optional[Cart]:
        """Execute cart retrieval."""
        try:
            # Try to get existing cart
            cart = Cart.objects.filter(customer=self.request.user).first()
            if cart:
                # Validate retrieved cart
                validate_command = ValidateCartCommand(cart)
                cart = validate_command.execute()
                
            # Create new cart if needed
            if not cart:
                cart = Cart.objects.create(customer=self.request.user)
                
            return cart
        except Exception as e:
            logger.error(f"Error retrieving cart: {str(e)}")
            return None

class GetCustomerCartCommand(BaseCommand[Optional[Cart]]):
    """Command for retrieving customer cart."""
    
    def __init__(self, customer: 'Customer'):
        super().__init__(None, None)
        self.customer = customer
        self._version_service = CartVersionService()
        
    def _execute(self) -> Optional[Cart]:
        """Execute customer cart retrieval."""
        try:
            cart = Cart.objects.filter(
                customer=self.customer,
                completed=False
            ).first()
            
            if cart:
                # Validate version
                cart, _ = self._version_service.get_cart_with_version(cart.id)
                
            return cart
        except Exception as e:
            logger.error(f"Error getting customer cart: {str(e)}")
            return None

class GetSessionCartCommand(BaseCommand[Optional[Cart]]):
    """Command for retrieving session cart."""
    
    def __init__(self, session_key: str):
        super().__init__(None, None)
        self.session_key = session_key
        self._version_service = CartVersionService()
        
    def _execute(self) -> Optional[Cart]:
        """Execute session cart retrieval."""
        try:
            cart = Cart.objects.filter(
                session_key=self.session_key,
                customer__isnull=True,
                completed=False
            ).first()
            
            if cart:
                # Validate version
                cart, _ = self._version_service.get_cart_with_version(cart.id)
                
            return cart
        except Exception as e:
            logger.error(f"Error getting session cart: {str(e)}")
            return None

class CreateCartCommand(BaseCommand[Cart]):
    """Command for creating a new cart."""
    
    def __init__(self, customer: Optional['Customer'] = None, session_key: Optional[str] = None):
        super().__init__(None, None)
        self.customer = customer
        self.session_key = session_key
        self._event_service = CartEventService()
        
    def _execute(self) -> Cart:
        """Execute cart creation."""
        try:
            with transaction.atomic():
                cart_data = {'version': 1}
                
                if self.customer:
                    # First check for existing uncompleted cart
                    existing_cart = Cart.objects.filter(
                        customer=self.customer,
                        completed=False
                    ).first()
                    if existing_cart:
                        return existing_cart
                        
                    cart_data['customer'] = self.customer
                elif self.session_key:
                    # First check for existing uncompleted cart
                    existing_cart = Cart.objects.filter(
                        session_key=self.session_key,
                        completed=False
                    ).first()
                    if existing_cart:
                        return existing_cart
                        
                    cart_data['session_key'] = self.session_key
                else:
                    raise ValidationError("Either customer or session_key must be provided")
                    
                cart = Cart.objects.create(**cart_data)
                
                # Log creation event
                self._event_service.log_event(
                    cart=cart,
                    event_type=CartEvent.CREATED
                )
                
                return cart
                
        except IntegrityError as e:
            logger.error(f"Error creating cart (integrity error): {str(e)}")
            # Try to get existing cart one more time in case of race condition
            if self.customer:
                cart = Cart.objects.filter(customer=self.customer, completed=False).first()
            else:
                cart = Cart.objects.filter(session_key=self.session_key, completed=False).first()
            if cart:
                return cart
            raise CartError("Failed to create cart - integrity error")
        except Exception as e:
            logger.error(f"Error creating cart: {str(e)}")
            raise CartError("Failed to create cart")

class MergeCartsCommand(BaseCommand[None]):
    """Command for merging guest cart into customer cart."""
    
    def __init__(self, customer_cart: Cart, guest_cart: Cart):
        strategy = MergeCartStrategy(customer_cart)
        super().__init__(customer_cart, strategy)
        self.guest_cart = guest_cart
        
    def _execute(self) -> None:
        """Execute cart merge with proper version control."""
        try:
            with transaction.atomic():
                # Execute merge strategy
                self.strategy.execute(self.guest_cart)
                
                # Clear items from guest cart
                self.guest_cart.items.all().delete()
                
                # Mark guest cart as completed
                self.guest_cart.completed = True
                self.guest_cart.completed_at = timezone.now()
                self.guest_cart.save(update_fields=['completed', 'completed_at'])
                
        except Exception as e:
            logger.error(f"Error executing merge carts command: {str(e)}")
            raise ValidationError(str(e))