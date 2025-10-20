"""Order API routes."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.order_dto import (
    OrderCreateDTO,
    OrderResponseDTO,
    OrderUpdateStatusDTO,
    OrderItemResponseDTO,
)
from src.domain.entities.order import Order, OrderStatus
from src.domain.entities.order_item import OrderItem
from src.domain.entities.user import User
from src.domain.value_objects.money import Money
from src.infrastructure.database.repositories.order_repository import OrderRepository
from src.infrastructure.database.session import get_db
from src.presentation.api.dependencies import get_current_user, require_admin

router = APIRouter()


@router.post("/", response_model=OrderResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_order(
    dto: OrderCreateDTO,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderResponseDTO:
    """Create a new order.

    Args:
        dto: Order creation data
        session: Database session
        current_user: Current authenticated user

    Returns:
        Created order data
    """
    repo = OrderRepository(session)

    # Create entity
    order = Order(
        customer_name=dto.customer_name,
        customer_email=dto.customer_email,
        notes=dto.notes,
        created_by_user_id=current_user.id,
    )

    # Add items
    for item_dto in dto.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_dto.product_id,
            quantity=item_dto.quantity,
            unit_price=Money(item_dto.unit_price, "USD"),
        )
        order.items.append(order_item)

    # Save to database
    created = await repo.create(order)

    # Calculate total
    total = created.calculate_total()

    return OrderResponseDTO(
        id=created.id,
        customer_name=created.customer_name,
        customer_email=created.customer_email,
        status=created.status.value,
        notes=created.notes,
        items=[
            OrderItemResponseDTO(
                id=item.id,
                product_id=item.product_id,
                product_name=None,  # Would need to join with products table
                quantity=item.quantity,
                unit_price=item.unit_price.amount,
                total=item.calculate_total().amount,
            )
            for item in created.items
        ],
        total=total.amount,
        created_at=created.created_at,
        updated_at=created.updated_at,
    )


@router.get("/", response_model=List[OrderResponseDTO])
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[OrderResponseDTO]:
    """List all orders.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        session: Database session
        current_user: Current authenticated user

    Returns:
        List of orders
    """
    repo = OrderRepository(session)

    # Admin sees all orders, regular users see only their own
    if current_user.is_admin():
        orders = await repo.get_all(skip, limit)
    else:
        orders = await repo.get_by_user_id(current_user.id, skip, limit)

    return [
        OrderResponseDTO(
            id=order.id,
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            status=order.status.value,
            notes=order.notes,
            items=[
                OrderItemResponseDTO(
                    id=item.id,
                    product_id=item.product_id,
                    product_name=None,
                    quantity=item.quantity,
                    unit_price=item.unit_price.amount,
                    total=item.calculate_total().amount,
                )
                for item in order.items
            ],
            total=order.calculate_total().amount,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
        for order in orders
    ]


@router.get("/{order_id}", response_model=OrderResponseDTO)
async def get_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderResponseDTO:
    """Get order by ID.

    Args:
        order_id: Order ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        Order data

    Raises:
        HTTPException: If order not found or access denied
    """
    repo = OrderRepository(session)
    order = await repo.get_with_items(order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # Check access: admin can see all, users can see only their own orders
    if not current_user.is_admin() and order.created_by_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return OrderResponseDTO(
        id=order.id,
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        status=order.status.value,
        notes=order.notes,
        items=[
            OrderItemResponseDTO(
                id=item.id,
                product_id=item.product_id,
                product_name=None,
                quantity=item.quantity,
                unit_price=item.unit_price.amount,
                total=item.calculate_total().amount,
            )
            for item in order.items
        ],
        total=order.calculate_total().amount,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.patch("/{order_id}/status", response_model=OrderResponseDTO)
async def update_order_status(
    order_id: UUID,
    dto: OrderUpdateStatusDTO,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> OrderResponseDTO:
    """Update order status (Admin only).

    Args:
        order_id: Order ID
        dto: Order status update data
        session: Database session
        current_user: Current authenticated admin user

    Returns:
        Updated order data

    Raises:
        HTTPException: If order not found
    """
    repo = OrderRepository(session)
    order = await repo.get_by_id(order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # Update status
    order.status = OrderStatus(dto.status)

    # Save changes
    updated = await repo.update(order)

    return OrderResponseDTO(
        id=updated.id,
        customer_name=updated.customer_name,
        customer_email=updated.customer_email,
        status=updated.status.value,
        notes=updated.notes,
        items=[
            OrderItemResponseDTO(
                id=item.id,
                product_id=item.product_id,
                product_name=None,
                quantity=item.quantity,
                unit_price=item.unit_price.amount,
                total=item.calculate_total().amount,
            )
            for item in updated.items
        ],
        total=updated.calculate_total().amount,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> None:
    """Delete order (Admin only).

    Args:
        order_id: Order ID
        session: Database session
        current_user: Current authenticated admin user

    Raises:
        HTTPException: If order not found
    """
    repo = OrderRepository(session)
    deleted = await repo.delete(order_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
