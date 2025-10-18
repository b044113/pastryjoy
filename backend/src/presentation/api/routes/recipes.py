"""Recipe API routes."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.recipe_dto import (
    RecipeCreateDTO,
    RecipeResponseDTO,
    RecipeUpdateDTO,
    RecipeIngredientResponseDTO,
)
from src.domain.entities.recipe import Recipe
from src.domain.entities.recipe_ingredient import RecipeIngredient
from src.domain.entities.user import User
from src.infrastructure.database.repositories.recipe_repository import RecipeRepository
from src.infrastructure.database.session import get_db
from src.presentation.api.dependencies import get_current_user, require_admin

router = APIRouter()


@router.post(
    "/", response_model=RecipeResponseDTO, status_code=status.HTTP_201_CREATED
)
async def create_recipe(
    dto: RecipeCreateDTO,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> RecipeResponseDTO:
    """Create a new recipe (Admin only).

    Args:
        dto: Recipe creation data
        session: Database session
        current_user: Current authenticated admin user

    Returns:
        Created recipe data
    """
    repo = RecipeRepository(session)

    # Create entity
    recipe = Recipe(
        name=dto.name,
        instructions=dto.instructions,
    )

    # Add ingredients
    for ingredient_dto in dto.ingredients:
        recipe_ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ingredient_dto.ingredient_id,
            quantity=ingredient_dto.quantity,
        )
        recipe.ingredients.append(recipe_ingredient)

    # Save to database
    created = await repo.create(recipe)

    return RecipeResponseDTO(
        id=created.id,
        name=created.name,
        instructions=created.instructions,
        ingredients=[
            RecipeIngredientResponseDTO(
                id=ing.id,
                ingredient_id=ing.ingredient_id,
                ingredient_name=None,  # Would need to join with ingredients table
                quantity=ing.quantity,
            )
            for ing in created.ingredients
        ],
        created_at=created.created_at,
        updated_at=created.updated_at,
    )


@router.get("/", response_model=List[RecipeResponseDTO])
async def list_recipes(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[RecipeResponseDTO]:
    """List all recipes.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        session: Database session
        current_user: Current authenticated user

    Returns:
        List of recipes
    """
    repo = RecipeRepository(session)
    recipes = await repo.get_all(skip, limit)

    return [
        RecipeResponseDTO(
            id=recipe.id,
            name=recipe.name,
            instructions=recipe.instructions,
            ingredients=[
                RecipeIngredientResponseDTO(
                    id=ing.id,
                    ingredient_id=ing.ingredient_id,
                    ingredient_name=None,
                    quantity=ing.quantity,
                )
                for ing in recipe.ingredients
            ],
            created_at=recipe.created_at,
            updated_at=recipe.updated_at,
        )
        for recipe in recipes
    ]


@router.get("/{recipe_id}", response_model=RecipeResponseDTO)
async def get_recipe(
    recipe_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecipeResponseDTO:
    """Get recipe by ID.

    Args:
        recipe_id: Recipe ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        Recipe data

    Raises:
        HTTPException: If recipe not found
    """
    repo = RecipeRepository(session)
    recipe = await repo.get_with_ingredients(recipe_id)

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    return RecipeResponseDTO(
        id=recipe.id,
        name=recipe.name,
        instructions=recipe.instructions,
        ingredients=[
            RecipeIngredientResponseDTO(
                id=ing.id,
                ingredient_id=ing.ingredient_id,
                ingredient_name=None,
                quantity=ing.quantity,
            )
            for ing in recipe.ingredients
        ],
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
    )


@router.put("/{recipe_id}", response_model=RecipeResponseDTO)
async def update_recipe(
    recipe_id: UUID,
    dto: RecipeUpdateDTO,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> RecipeResponseDTO:
    """Update recipe (Admin only).

    Args:
        recipe_id: Recipe ID
        dto: Recipe update data
        session: Database session
        current_user: Current authenticated admin user

    Returns:
        Updated recipe data

    Raises:
        HTTPException: If recipe not found
    """
    repo = RecipeRepository(session)
    recipe = await repo.get_by_id(recipe_id)

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # Update fields
    if dto.name is not None:
        recipe.name = dto.name
    if dto.instructions is not None:
        recipe.instructions = dto.instructions

    # Save changes
    updated = await repo.update(recipe)

    return RecipeResponseDTO(
        id=updated.id,
        name=updated.name,
        instructions=updated.instructions,
        ingredients=[
            RecipeIngredientResponseDTO(
                id=ing.id,
                ingredient_id=ing.ingredient_id,
                ingredient_name=None,
                quantity=ing.quantity,
            )
            for ing in updated.ingredients
        ],
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> None:
    """Delete recipe (Admin only).

    Args:
        recipe_id: Recipe ID
        session: Database session
        current_user: Current authenticated admin user

    Raises:
        HTTPException: If recipe not found
    """
    repo = RecipeRepository(session)
    deleted = await repo.delete(recipe_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )
