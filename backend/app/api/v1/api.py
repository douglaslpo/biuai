from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    tenants,
    fiis
)

api_router = APIRouter()

# Auth routes
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"]
)

# User routes
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

# Tenant routes
api_router.include_router(
    tenants.router,
    prefix="/tenants",
    tags=["tenants"]
)

# FII routes
api_router.include_router(
    fiis.router,
    prefix="/fiis",
    tags=["fiis"]
) 