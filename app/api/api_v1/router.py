from fastapi import APIRouter
from .routers import (
    users,
    users_ws,
    shadow_questions,
    shadow_answers,
    skips
)

api_v1_router = APIRouter()

api_v1_router.include_router(users.router, prefix="/users", tags=["users"])
api_v1_router.include_router(users_ws.router, prefix="/usersWs", tags=["users_ws"])
api_v1_router.include_router(shadow_questions.router, prefix="/shadowQuestions", tags=["shadow_questions"])
api_v1_router.include_router(shadow_answers.router, prefix="/shadowAnswers", tags=["shadow_answers"])
api_v1_router.include_router(skips.router, prefix="/skips", tags=["skips"])