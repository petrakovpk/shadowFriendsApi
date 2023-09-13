from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from firebase_admin import auth, messaging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

import crud
from config import get_db, get_firebase_auth
from helpers import check_user_authorization, check_object_authorization
from schemas import UserBase, UserCreate, UserUpdate, User, ShadowQuestion, ShadowAnswer

router = APIRouter()

@router.get("", response_model=List[User], status_code=200)
async def get_users(
        db: AsyncSession = Depends(get_db),
        firebase_user: auth.UserRecord = Depends(get_firebase_auth)
):
    check_user_authorization(firebase_user)

    users_in_db = await crud.users.get_users(db=db)
    return users_in_db

@router.put("/{user_uid}", response_model=User, status_code=200)
async def update_user(
        user_uid: str,
        user: UserBase,
        db: AsyncSession = Depends(get_db),
        firebase_user: auth.UserRecord = Depends(get_firebase_auth)
):
    check_user_authorization(firebase_user)

    if user_uid != firebase_user.uid:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_in_db = await crud.users.get_user(db=db, user_uid=user_uid)

    if user_in_db is None:
        user_create = UserCreate(**user.__dict__)
        result = await crud.users.create_user(db=db, user=user_create)
        return result

    if user_in_db.uid != firebase_user.uid:
        raise HTTPException(status_code=403, detail="Forbidden")

    user_update = UserUpdate(**user.__dict__)
    user_update.last_activity = datetime.now()
    result = await crud.users.update_user(db=db, user=user_update)

    return result

@router.get("/{user_uid}/recommendedShadowQuestions", response_model=List[ShadowQuestion], status_code=200)
async def get_recommended_shadow_questions(
        user_uid: str,
        db: AsyncSession = Depends(get_db),
        firebase_user: auth.UserRecord = Depends(get_firebase_auth)
):
    check_user_authorization(firebase_user)

    result = await crud.users.get_recommended_shadow_questions(db=db, user_uid=user_uid)
    return result


@router.get("/{user_uid}/shadowQuestions", response_model=List[ShadowQuestion], status_code=200)
async def get_shadow_questions(
        user_uid: str,
        db: AsyncSession = Depends(get_db),
        firebase_user: auth.UserRecord = Depends(get_firebase_auth)
):
    check_user_authorization(firebase_user)

    result = await crud.users.get_shadow_questions(db=db, user_uid=user_uid)
    return result


@router.get("/{user_uid}/shadowQuestions/shadowAnswers", response_model=List[ShadowAnswer], status_code=200)
async def get_shadow_questions_shadow_answers(
        user_uid: str,
        db: AsyncSession = Depends(get_db),
        firebase_user: auth.UserRecord = Depends(get_firebase_auth)
):
    check_user_authorization(firebase_user)

    result = await crud.shadow_answers.get_shadow_questions_shadow_answers(db=db, user_uid=user_uid)
    return result
