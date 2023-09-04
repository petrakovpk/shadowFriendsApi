from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from firebase_admin import auth
from pydantic import UUID4

import crud
from config import get_db, get_firebase_auth
from helpers import check_user_authorization, check_object_authorization
from schemas import ShadowAnswerCreate, ShadowAnswerUpdate, ShadowAnswer

router = APIRouter()

@router.get("/{shadow_answer_uuid}", response_model=ShadowAnswer, status_code=200)
async def get_shadow_answer(
        shadow_answer_uuid: UUID4,
        db: Session = Depends(get_db),
        firebase_user: auth.UserRecord = Depends(get_firebase_auth)
):
    check_user_authorization(firebase_user)

    shadow_answer_in_db = await crud.shadow_answers.get_shadow_answer(db=db, shadow_answer_uuid=shadow_answer_uuid)

    if shadow_answer_in_db is None:
        raise HTTPException(status_code=404, detail="Not found")

    return shadow_answer_in_db

@router.put("/{shadow_answer_uuid}", response_model=ShadowAnswer, status_code=200)
async def update_shadow_answer(
        shadow_answer_uuid: UUID4,
        shadow_answer: ShadowAnswer,
        db: Session = Depends(get_db),
        firebase_user: auth.UserRecord = Depends(get_firebase_auth)
):
    check_user_authorization(firebase_user)

    shadow_answer_in_db = await crud.shadow_answers.get_shadow_answer(db=db, shadow_answer_uuid=shadow_answer_uuid)

    if shadow_answer_in_db is None:
        shadow_answer_create = ShadowAnswerCreate(**shadow_answer.__dict__)
        await crud.shadow_answers.create_shadow_answer(db=db, shadow_answer=shadow_answer_create)
        return shadow_answer_create

    check_object_authorization(shadow_answer_in_db, firebase_user)

    shadow_answer_update = ShadowAnswerUpdate(**shadow_answer.__dict__)
    result = await crud.shadow_answers.update_shadow_answer(db=db, shadow_answer_uuid=shadow_answer_uuid, shadow_answer=shadow_answer_update)

    return result