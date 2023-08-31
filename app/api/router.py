from fastapi import APIRouter
from .api_v1 import api_v1_router

router = APIRouter()

router.include_router(api_v1_router, prefix="/v1.0", tags=["api_v1_router"])
