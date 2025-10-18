"""Product API routes."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.product_dto import (
    ProductCreateDTO,
    ProductResponseDTO,
    ProductUpdateDTO,
    ProductRecipeResponseDTO,
)
from src.domain.entities.product import Product, ProductRecipe
from src.domain.entities.user import User
from src.domain.value_objects.money import Money
from src.infrastructure.database.repositories.product_repository import ProductRepository
from src.infrastructure.database.session import get_db
from src.presentation.api.dependencies import get_current_user, require_admin

router = APIRouter()


@router.post(
    "/", response_model=ProductResponseDTO, status_code=status.HTTP_201_CREATED
)
async def create_product(
    dto: ProductCreateDTO,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> ProductResponseDTO:
    """Create a new product (Admin only).

    Args:
        dto: Product creation data
        session: Database session
        current_user: Current authenticated admin user

    Returns:
        Created product data
    """
    repo = ProductRepository(session)

    # Create entity
    product = Product(
        name=dto.name,
        image_url=dto.image_url,
        fixed_costs=Money(dto.fixed_costs, "USD"),
        variable_costs_percentage=dto.variable_costs_percentage,
        profit_margin_percentage=dto.profit_margin_percentage,
    )

    # Add recipes
    for recipe_dto in dto.recipes:
        product_recipe = ProductRecipe(
            recipe_id=recipe_dto.recipe_id,
            quantity=recipe_dto.quantity,
        )
        product.recipes.append(product_recipe)

    # Save to database
    created = await repo.create(product)

    return ProductResponseDTO(
        id=created.id,
        name=created.name,
        image_url=created.image_url,
        fixed_costs=created.fixed_costs.amount,
        variable_costs_percentage=created.variable_costs_percentage,
        profit_margin_percentage=created.profit_margin_percentage,
        recipes=[
            ProductRecipeResponseDTO(
                recipe_id=rec.recipe_id,
                recipe_name=None,  # Would need to join with recipes table
                quantity=rec.quantity,
            )
            for rec in created.recipes
        ],
        created_at=created.created_at,
        updated_at=created.updated_at,
    )


@router.get("/", response_model=List[ProductResponseDTO])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ProductResponseDTO]:
    """List all products.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        session: Database session
        current_user: Current authenticated user

    Returns:
        List of products
    """
    repo = ProductRepository(session)
    products = await repo.get_all(skip, limit)

    return [
        ProductResponseDTO(
            id=product.id,
            name=product.name,
            image_url=product.image_url,
            fixed_costs=product.fixed_costs.amount,
            variable_costs_percentage=product.variable_costs_percentage,
            profit_margin_percentage=product.profit_margin_percentage,
            recipes=[
                ProductRecipeResponseDTO(
                    recipe_id=rec.recipe_id,
                    recipe_name=None,
                    quantity=rec.quantity,
                )
                for rec in product.recipes
            ],
            created_at=product.created_at,
            updated_at=product.updated_at,
        )
        for product in products
    ]


@router.get("/{product_id}", response_model=ProductResponseDTO)
async def get_product(
    product_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductResponseDTO:
    """Get product by ID.

    Args:
        product_id: Product ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        Product data

    Raises:
        HTTPException: If product not found
    """
    repo = ProductRepository(session)
    product = await repo.get_with_recipes(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return ProductResponseDTO(
        id=product.id,
        name=product.name,
        image_url=product.image_url,
        fixed_costs=product.fixed_costs.amount,
        variable_costs_percentage=product.variable_costs_percentage,
        profit_margin_percentage=product.profit_margin_percentage,
        recipes=[
            ProductRecipeResponseDTO(
                recipe_id=rec.recipe_id,
                recipe_name=None,
                quantity=rec.quantity,
            )
            for rec in product.recipes
        ],
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


@router.put("/{product_id}", response_model=ProductResponseDTO)
async def update_product(
    product_id: UUID,
    dto: ProductUpdateDTO,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> ProductResponseDTO:
    """Update product (Admin only).

    Args:
        product_id: Product ID
        dto: Product update data
        session: Database session
        current_user: Current authenticated admin user

    Returns:
        Updated product data

    Raises:
        HTTPException: If product not found
    """
    repo = ProductRepository(session)
    product = await repo.get_by_id(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # Update fields
    if dto.name is not None:
        product.name = dto.name
    if dto.image_url is not None:
        product.image_url = dto.image_url
    if dto.fixed_costs is not None:
        product.fixed_costs = Money(dto.fixed_costs, "USD")
    if dto.variable_costs_percentage is not None:
        product.variable_costs_percentage = dto.variable_costs_percentage
    if dto.profit_margin_percentage is not None:
        product.profit_margin_percentage = dto.profit_margin_percentage

    # Save changes
    updated = await repo.update(product)

    return ProductResponseDTO(
        id=updated.id,
        name=updated.name,
        image_url=updated.image_url,
        fixed_costs=updated.fixed_costs.amount,
        variable_costs_percentage=updated.variable_costs_percentage,
        profit_margin_percentage=updated.profit_margin_percentage,
        recipes=[
            ProductRecipeResponseDTO(
                recipe_id=rec.recipe_id,
                recipe_name=None,
                quantity=rec.quantity,
            )
            for rec in updated.recipes
        ],
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> None:
    """Delete product (Admin only).

    Args:
        product_id: Product ID
        session: Database session
        current_user: Current authenticated admin user

    Raises:
        HTTPException: If product not found
    """
    repo = ProductRepository(session)
    deleted = await repo.delete(product_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
