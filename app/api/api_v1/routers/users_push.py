import asyncio
import json
from datetime import datetime
from firebase_admin import auth, messaging
from sqlalchemy import event
from sqlalchemy.ext.declarative import DeclarativeMeta
import weakref
import dateutil.parser

from uuid import UUID

import crud
from db import AsyncSessionLocal
from models import ShadowQuestionInDb, ShadowAnswerInDb
from schemas import ShadowQuestion, ShadowAnswer

@event.listens_for(ShadowQuestionInDb, 'after_insert')
def shadow_question_after_insert_listener(mapper, connection, target):
    asyncio.create_task(send_shadow_question_push(target))

@event.listens_for(ShadowQuestionInDb, 'after_update')
def shadow_question_after_update_listener(mapper, connection, target):
    asyncio.create_task(send_shadow_question_push(target))

@event.listens_for(ShadowAnswerInDb, 'after_insert')
def shadow_question_after_insert_listener(mapper, connection, target):
    asyncio.create_task(send_shadow_answer_push(target))

@event.listens_for(ShadowAnswerInDb, 'after_update')
def shadow_question_after_update_listener(mapper, connection, target):
    asyncio.create_task(send_shadow_answer_push(target))

async def send_shadow_question_push(shadow_question_in_db: ShadowQuestionInDb):
    async with AsyncSessionLocal() as db:
        user_in_db = await crud.users.get_user(db=db, user_uid=shadow_question_in_db.user_uid)

        shadow_question = ShadowQuestion(**shadow_question_in_db.__dict__)
        body = shadow_question.model_dump_json()
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
    async with AsyncSessionLocal() as db:
        shadow_question_in_db = await crud.shadow_questions.get_shadow_question(db=db, shadow_question_uuid=shadow_answer_in_db.shadow_question_uuid)
        user_in_db = await crud.users.get_user(db=db, user_uid=shadow_question_in_db.user_uid)

        shadow_answer = ShadowAnswer(**shadow_question_in_db.__dict__)
        body = shadow_answer.model_dump_json()
        message = messaging.Message(
            notification=messaging.Notification(
                title="shadow_answer",
                body=body
            ),
            token=user_in_db.fcm_token
        )

        response = messaging.send(message)
        return response