from fastapi import APIRouter
from .routers import (
    users,
    shadow_questions,
    shadow_answers,
    skips
)

api_v1_router = APIRouter()

api_v1_router.include_router(users.router, prefix="/users", tags=["users"])
api_v1_router.include_router(shadow_questions.router, prefix="/shadow_questions", tags=["shadow_questions"])
api_v1_router.include_router(shadow_answers.router, prefix="/shadow_answers", tags=["shadow_answers"])
api_v1_router.include_router(skips.router, prefix="/skips", tags=["skips"])