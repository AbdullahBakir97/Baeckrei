"""
Product Management Controllers.
This module provides controllers for handling product-related operations.
"""

from .PMC import ProductManagementController

# Export the unified controller as the main interface
__all__ = ['ProductManagementController']

# Create a default instance for easy import
default_controller = ProductManagementController()