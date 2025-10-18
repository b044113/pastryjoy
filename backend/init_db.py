"""Initialize database tables."""
import asyncio
from src.infrastructure.database.session import Base, async_engine
from src.infrastructure.database.models import (
    user,
    ingredient,
    ingredient_cost,
    recipe,
    product,
    order,
)

async def init_db():
    """Create all database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())
