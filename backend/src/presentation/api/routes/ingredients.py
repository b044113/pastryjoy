"""Ingredient API routes."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.ingredient_dto import (
    IngredientCreateDTO,
    IngredientResponseDTO,
    IngredientUpdateDTO,
)
from src.domain.entities.ingredient import Ingredient
from src.domain.entities.user import User
from src.domain.value_objects.measurement_unit import MeasurementUnit
from src.infrastructure.database.repositories.ingredient_repository import (
    IngredientRepository,
)
from src.infrastructure.database.session import get_db
from src.presentation.api.dependencies import get_current_user, require_admin

router = APIRouter()


@router.post(
    "/", response_model=IngredientResponseDTO, status_code=status.HTTP_201_CREATED
)
async def create_ingredient(
    dto: IngredientCreateDTO,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> IngredientResponseDTO:
    """Create a new ingredient (Admin only).

    Args:
        dto: Ingredient creation data
        session: Database session
        current_user: Current authenticated admin user

    Returns:
        Created ingredient data
    """
    from sqlalchemy.exc import IntegrityError

    repo = IngredientRepository(session)

    # Create entity
    ingredient = Ingredient(
        name=dto.name,
        unit=MeasurementUnit(dto.unit),
    )

    # Save to database
    try:
        created = await repo.create(ingredient)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ingredient with name '{dto.name}' already exists",
        )

    return IngredientResponseDTO(
        id=created.id,
        name=created.name,
        unit=created.unit.value,
        created_at=created.created_at,
        updated_at=created.updated_at,
    )


@router.get("/", response_model=List[IngredientResponseDTO])
async def list_ingredients(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[IngredientResponseDTO]:
    """List all ingredients.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        session: Database session
        current_user: Current authenticated user

    Returns:
        List of ingredients
    """
    repo = IngredientRepository(session)
    ingredients = await repo.get_all(skip, limit)

    return [
        IngredientResponseDTO(
            id=ing.id,
            name=ing.name,
            unit=ing.unit.value,
            created_at=ing.created_at,
            updated_at=ing.updated_at,
        )
        for ing in ingredients
    ]


@router.get("/{ingredient_id}", response_model=IngredientResponseDTO)
async def get_ingredient(
    ingredient_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IngredientResponseDTO:
    """Get ingredient by ID.

    Args:
        ingredient_id: Ingredient ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        Ingredient data

    Raises:
        HTTPException: If ingredient not found
    """
    repo = IngredientRepository(session)
    ingredient = await repo.get_by_id(ingredient_id)

    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found",
        )

    return IngredientResponseDTO(
        id=ingredient.id,
        name=ingredient.name,
        unit=ingredient.unit.value,
        created_at=ingredient.created_at,
        updated_at=ingredient.updated_at,
    )


@router.put("/{ingredient_id}", response_model=IngredientResponseDTO)
async def update_ingredient(
    ingredient_id: UUID,
    dto: IngredientUpdateDTO,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> IngredientResponseDTO:
    """Update ingredient (Admin only).

    Args:
        ingredient_id: Ingredient ID
        dto: Ingredient update data
        session: Database session
        current_user: Current authenticated admin user

    Returns:
        Updated ingredient data

    Raises:
        HTTPException: If ingredient not found
    """
    repo = IngredientRepository(session)
    ingredient = await repo.get_by_id(ingredient_id)

    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found",
        )

    # Update fields
    if dto.name is not None:
        ingredient.name = dto.name
    if dto.unit is not None:
        ingredient.unit = MeasurementUnit(dto.unit)

    # Save changes
    updated = await repo.update(ingredient)

    return IngredientResponseDTO(
        id=updated.id,
        name=updated.name,
        unit=updated.unit.value,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ingredient(
    ingredient_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> None:
    """Delete ingredient (Admin only).

    Args:
        ingredient_id: Ingredient ID
        session: Database session
        current_user: Current authenticated admin user

    Raises:
        HTTPException: If ingredient not found
    """
    repo = IngredientRepository(session)
    deleted = await repo.delete(ingredient_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found",
        )
