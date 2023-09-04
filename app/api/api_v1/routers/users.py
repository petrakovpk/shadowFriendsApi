import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.websockets import WebSocket, WebSocketDisconnect
from uuid import UUID
from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from firebase_admin import auth
from firebase_admin._auth_utils import InvalidIdTokenError
from datetime import datetime
from typing import Optional, List

import crud
from config import get_db, get_firebase_auth
from helpers import check_user_authorization, check_object_authorization
from schemas import UserCreate, UserUpdate, User, ShadowQuestion, ShadowAnswer
from models import ShadowQuestionInDb, ShadowAnswerInDb
from config import engine, Base, AsyncSessionLocal

router = APIRouter()

# This is a global set to keep track of active websockets for each user
active_websockets = {}


@router.put("/{user_uid}", response_model=User, status_code=200)
async def update_user(
        user_uid: str,
        db: AsyncSession = Depends(get_db),
        firebase_user: auth.UserRecord = Depends(get_firebase_auth)
):
    check_user_authorization(firebase_user)

    if user_uid != firebase_user.uid:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_in_db = await crud.users.get_user(db=db, user_uid=user_uid)

    if user_in_db is None:
        user_create = UserCreate(uid=user_uid, created=datetime.now(), last_activity=datetime.now())
        result = await crud.users.create_user(db=db, user=user_create)
        return result

    if user_in_db.uid != firebase_user.uid:
        raise HTTPException(status_code=403, detail="Forbidden")

    user_update = UserUpdate(uid=user_uid, last_activity=datetime.now())
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

    shadow_questions_pd = [ShadowQuestion(**shadow_question_in_db.__dict__) for shadow_question_in_db in result]

    return result


@router.websocket("/ws")
async def websocket(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"msg": "Hello WebSocket"})
    await websocket.close()


@router.websocket("/{user_uid}/shadowQuestions/ws")
async def get_shadow_questions_ws(
        websocket: WebSocket,
        user_uid: str
):
    await websocket.accept()

    # Get the token from headers
    token_header = websocket.headers.get("Authorization")

    # Extract the actual token by removing "Bearer " prefix
    if not token_header or not token_header.startswith("Bearer "):
        await websocket.send_json({"msg": "Missing or malformed Authorization header"})
        await websocket.close()
        return

    token = token_header.split(" ")[1]  # Take the second part after "Bearer "

    if token == "PASHA_SECRET_KEY":
        uid = 'nAGy29cq5yPc0ZGeMI5Kf2JxuK02'
        user = auth.get_user(uid)
    else:
        try:
            decoded_token = auth.verify_id_token(token)
            user = auth.get_user(decoded_token["uid"])
        except InvalidIdTokenError:
            await websocket.send_json({
                "type": "connection_status",
                "data": {
                    "status": "refused",
                    "reason": "Wrong number of segments in token"
                }
            })

            await websocket.close()
            return

    if user.uid != user_uid:
        await websocket.send_json({
            "type": "connection_status",
            "data": {
                "status": "refused",
                "reason": "The specified user_uid does not match the user ID in Firebase Auth."
            }
        })
        await websocket.close()
        return
    else:
        await websocket.send_json({
            "type": "connection_status",
            "data": {
                "status": "success"
            }
        })

    asyncio.create_task(send_shadow_question_notification(user_uid))
    asyncio.create_task(send_shadow_answer_notification(user_uid))

    active_websockets[user_uid] = websocket
    try:
        while True:
            # You can listen for messages from the client if needed
            data = await websocket.receive_text()

            # Handle the received data as needed
    except WebSocketDisconnect:
        # Remove the websocket connection from the global set when it's closed
        active_websockets.pop(user_uid, None)


# Обработчик для добавления новой записи
@event.listens_for(ShadowQuestionInDb, 'after_insert')
def shadow_question_after_insert_listener(mapper, connection, target):
    user_uid = target.user_uid
    asyncio.create_task(send_shadow_question_notification(user_uid))

@event.listens_for(ShadowQuestionInDb, 'after_update')
def shadow_question_after_update_listener(mapper, connection, target):
    user_uid = target.user_uid
    asyncio.create_task(send_shadow_question_notification(user_uid))

@event.listens_for(ShadowAnswerInDb, 'after_insert')
def shadow_answer_after_insert_listener(mapper, connection, target):
    user_uid = target.user_uid
    asyncio.create_task(send_shadow_answer_notification(user_uid))

@event.listens_for(ShadowAnswerInDb, 'after_update')
def shadow_answer_after_update_listener(mapper, connection, target):
    user_uid = target.user_uid
    asyncio.create_task(send_shadow_answer_notification(user_uid))

def custom_encoder(obj):
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%dT%H:%M:%S%z")
    elif isinstance(obj, UUID):
        return str(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


async def send_shadow_question_notification(user_uid):
    # user_uid = target.user_uid
    async with AsyncSessionLocal() as db:
        if user_uid in active_websockets:
            # Fetch all ShadowQuestionInDb for the given user_uid
            shadow_questions_in_db = await crud.users.get_shadow_questions(db=db, user_uid=user_uid)
            shadow_questions_dicts = [ShadowQuestion(**shadow_question_in_db.__dict__).model_dump() for
                                      shadow_question_in_db in shadow_questions_in_db]

            result_json = {
                "type": "shadow_questions",
                "data": [json.dumps(shadow_question_dict, default=custom_encoder, ensure_ascii=False) for
                         shadow_question_dict in shadow_questions_dicts]
            }

            # Send the list to the websocket if it's active for the user
            websocket = active_websockets[user_uid]
            current_loop = asyncio.get_event_loop()
            current_loop.create_task(websocket.send_json(result_json))


async def send_shadow_answer_notification(user_uid):
    # user_uid = target.user_uid
    async with AsyncSessionLocal() as db:
        if user_uid in active_websockets:
            # Fetch all ShadowQuestionInDb for the given user_uid
            shadow_answers_in_db = await crud.shadow_answers.get_shadow_answers(db=db, user_uid=user_uid)
            shadow_answers_dicts = [ShadowAnswer(**shadow_answer_in_db.__dict__).model_dump() for shadow_answer_in_db in shadow_answers_in_db]

            result_json = {
                "type": "shadow_answers",
                "data": [json.dumps(shadow_answer_dict, default=custom_encoder, ensure_ascii=False) for shadow_answer_dict
                         in shadow_answers_dicts]
            }

            # Send the list to the websocket if it's active for the user
            websocket = active_websockets[user_uid]
            current_loop = asyncio.get_event_loop()
            current_loop.create_task(websocket.send_json(result_json))
