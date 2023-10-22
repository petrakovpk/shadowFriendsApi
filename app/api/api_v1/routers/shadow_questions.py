from datetime import datetime
from firebase_admin import auth
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated,List
from pydantic import UUID4

import crud
from db import get_db
from firebase import get_firebase_auth
from helpers import check_user_authorization, check_object_authorization
from schemas import ShadowQuestionCreate, ShadowQuestionUpdate, ShadowQuestion, ShadowAnswer, ListUUID

router = APIRouter()

@router.get("/{shadow_question_uuid}", response_model=ShadowQuestion, status_code=200)
async def get_shadow_question(
        shadow_question_uuid: UUID4,
        db: Session = Depends(get_db),
        firebase_user: auth.UserRecord = Depends(get_firebase_auth)
):
    check_user_authorization(firebase_user)

    shadow_question_in_db = await crud.shadow_questions.get_shadow_question(db=db, shadow_question_uuid=shadow_question_uuid)

    if shadow_question_in_db is None:
        raise HTTPException(status_code=404, detail="Not found")

    return shadow_question_in_db

@router.get("/shadowAnswers/", response_model=List[ShadowAnswer], status_code=200)
async def get_shadow_answers(
        shadow_questions_uuid: ListUUID,
        db: Session = Depends(get_db),
        firebase_user: auth.UserRecord = Depends(get_firebase_auth)
):
    check_user_authorization(firebase_user)

    shadow_answers_in_db = await crud.shadow_questions.get_shadow_answers(
        db=db,
        shadow_questions_uuid=shadow_questions_uuid.uuids
    )

    return shadow_answers_in_db

@router.put("/{shadow_question_uuid}", response_model=ShadowQuestion, status_code=200)
async def update_shadow_question(
        shadow_question_uuid: UUID4,
        shadow_question: ShadowQuestion,
        db: Session = Depends(get_db),
        firebase_user: auth.UserRecord = Depends(get_firebase_auth)
):

    check_user_authorization(firebase_user)

    shadow_question_in_db = await crud.shadow_questions.get_shadow_question(db=db, shadow_question_uuid=shadow_question_uuid)

    if shadow_question_in_db is None:
        shadow_question_create = ShadowQuestionCreate(**shadow_question.__dict__)
        shadow_question_create.upload_date = datetime.now().replace(microsecond=0)
        result = await crud.shadow_questions.create_shadow_question(db=db, shadow_question=shadow_question_create)
        return result

    check_object_authorization(shadow_question_in_db, firebase_user)

    shadow_question_update = ShadowQuestionUpdate(**shadow_question.__dict__)
    shadow_question_update.upload_date = datetime.now().replace(microsecond=0)
    result = await crud.shadow_questions.update_shadow_question(db=db, shadow_question_uuid=shadow_question_uuid, shadow_question=shadow_question_update)

    return result