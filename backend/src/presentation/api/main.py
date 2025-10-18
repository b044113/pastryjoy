"""FastAPI main application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.config import get_settings
from src.presentation.api.routes import auth, ingredients, recipes, products, orders

settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="PastryJoy API",
    description="Bakery Management System REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(ingredients.router, prefix="/api/ingredients", tags=["Ingredients"])
app.include_router(recipes.router, prefix="/api/recipes", tags=["Recipes"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "message": "PastryJoy API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "service": "pastryjoy-api"}
