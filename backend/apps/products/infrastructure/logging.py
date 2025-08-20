import logging
import json
from functools import wraps
from typing import Any, Callable, Dict
from datetime import datetime
import traceback

class ProductLogger:
    """Custom logger for the products module"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add file handler
        file_handler = logging.FileHandler('products.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Set default level
        self.logger.setLevel(logging.INFO)

    def log_operation(self, operation_type: str) -> Callable:
        """Decorator to log operation details"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                start_time = datetime.now()
                operation_id = f"{operation_type}_{start_time.timestamp()}"
                
                # Log operation start
                self.logger.info(
                    f"Operation started: {operation_id}",
                    extra={
                        'operation_type': operation_type,
                        'operation_id': operation_id,
                        'args': args,
                        'kwargs': kwargs
                    }
                )
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Log successful operation
                    duration = (datetime.now() - start_time).total_seconds()
                    self.logger.info(
                        f"Operation completed: {operation_id}",
                        extra={
                            'operation_type': operation_type,
                            'operation_id': operation_id,
                            'duration': duration,
                            'status': 'success'
                        }
                    )
                    
                    return result
                    
                except Exception as e:
                    # Log failed operation
                    duration = (datetime.now() - start_time).total_seconds()
                    self.logger.error(
                        f"Operation failed: {operation_id}",
                        extra={
                            'operation_type': operation_type,
                            'operation_id': operation_id,
                            'duration': duration,
                            'status': 'error',
                            'error': str(e),
                            'traceback': traceback.format_exc()
                        }
                    )
                    raise
                    
            return wrapper
        return decorator

    def log_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log an event with details"""
        self.logger.info(
            f"Event occurred: {event_type}",
            extra={
                'event_type': event_type,
                'event_details': details,
                'timestamp': datetime.now().isoformat()
            }
        )

    def log_error(self, error_type: str, error: Exception, context: Dict[str, Any]) -> None:
        """Log an error with context"""
        self.logger.error(
            f"Error occurred: {error_type}",
            extra={
                'error_type': error_type,
                'error_message': str(error),
                'error_traceback': traceback.format_exc(),
                'context': context,
                'timestamp': datetime.now().isoformat()
            }
        )

# Create logger instance
product_logger = ProductLogger('products')
