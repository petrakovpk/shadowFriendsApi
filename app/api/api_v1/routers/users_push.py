import asyncio
from firebase_admin import auth, messaging
from pydantic import ValidationError
from sqlalchemy import event

import crud
from db import AsyncSessionLocal, session
from models import ShadowQuestionInDb, ShadowAnswerInDb
from schemas import ShadowQuestion, ShadowAnswer

@event.listens_for(ShadowQuestionInDb, 'after_insert')
@event.listens_for(ShadowQuestionInDb, 'after_update')
def shadow_question_listener(mapper, connection, target):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        loop.create_task(send_shadow_question_push(target))

    else:
        asyncio.run(send_shadow_question_push(target))

@event.listens_for(ShadowAnswerInDb, 'after_insert')
@event.listens_for(ShadowAnswerInDb, 'after_update')
def shadow_answer_listener(mapper, connection, target):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        loop.create_task(send_shadow_answer_push(target))

    else:
        asyncio.run(send_shadow_answer_push(target))

async def send_shadow_question_push(shadow_question_in_db: ShadowQuestionInDb):
    try:
        shadow_question = ShadowQuestion(**shadow_question_in_db.__dict__)
    except ValidationError:
        print(ValidationError)
        return

    user_in_db = await crud.users.get_user(db=session, user_uid=shadow_question_in_db.user_uid)

    body = shadow_question.json()
    message = messaging.Message(
        notification=messaging.Notification(
            title="shadow_question",
            body=body
        ),
        token=user_in_db.fcm_token
    )

    response = messaging.send(message)
    return response

async def send_shadow_answer_push(shadow_answer_in_db: ShadowAnswerInDb):
    try:
        shadow_answer = ShadowAnswer(**shadow_answer_in_db.__dict__)
    except ValidationError:
        print(ValidationError)
        return

    shadow_question_in_db = await crud.shadow_questions.get_shadow_question(db=session, shadow_question_uuid=shadow_answer.shadow_question_uuid)
    user_in_db = await crud.users.get_user(db=session, user_uid=shadow_question_in_db.user_uid)

    message = messaging.Message(
        notification=messaging.Notification(
            title="shadow_answer",
            body=shadow_answer.model_dump_json()
        ),
        token=user_in_db.fcm_token
    )

    response = messaging.send(message)
    return response