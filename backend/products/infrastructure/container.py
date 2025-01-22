from dependency_injector import containers, providers
from typing import Type

from .repositories import (
    DjangoProductRepository,
    DjangoCategoryRepository,
    DjangoIngredientRepository,
    DjangoAllergenRepository
)
from .unit_of_work import DjangoUnitOfWork
from ..domain.event_publisher import DomainEventPublisher
from ..services.product_service import ProductService
from ..controllers.PMC import ProductManagementController

class Container(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()

    # Infrastructure
    event_publisher = providers.Singleton(
        DomainEventPublisher
    )

    unit_of_work = providers.Factory(
        DjangoUnitOfWork
    )

    # Repositories
    product_repository = providers.Factory(
        DjangoProductRepository
    )

    category_repository = providers.Factory(
        DjangoCategoryRepository
    )

    ingredient_repository = providers.Factory(
        DjangoIngredientRepository
    )

    allergen_repository = providers.Factory(
        DjangoAllergenRepository
    )

    # Services
    product_service = providers.Factory(
        ProductService,
        unit_of_work=unit_of_work,
        event_publisher=event_publisher
    )

    # Controllers
    product_management_controller = providers.Factory(
        ProductManagementController,
        product_service=product_service
    )
