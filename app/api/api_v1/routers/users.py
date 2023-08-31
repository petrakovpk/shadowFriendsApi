import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.websockets import WebSocket, WebSocketDisconnect
from uuid import UUID
from sqlalchemy import event
from sqlalchemy.orm import Session
from firebase_admin import auth
from datetime import datetime
from typing import Optional, List


import crud
from config import get_db, get_firebase_auth
from helpers import check_user_authorization, check_object_authorization
from schemas import UserCreate, UserUpdate, User, ShadowQuestion
from models import ShadowQuestionInDb
from config import session, engine, Base

router = APIRouter()

# This is a global set to keep track of active websockets for each user
active_websockets = {}

@router.put("/{user_uid}", response_model=User, status_code=200)
async def update_user(
        user_uid: str,
        db: Session = Depends(get_db),
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
        db: Session = Depends(get_db),
        firebase_user: auth.UserRecord = Depends(get_firebase_auth)
):
    check_user_authorization(firebase_user)

    result = await crud.users.get_recommended_shadow_questions(db=db, user_uid=user_uid)
    return result

@router.get("/{user_uid}/shadowQuestions", response_model=List[ShadowQuestion], status_code=200)
async def get_shadow_questions(
        user_uid: str,
        db: Session = Depends(get_db),
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
    await websocket.send_json({"msg": "Hello WebSocket"})
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
def after_insert_listener(mapper, connection, target):
    asyncio.create_task(send_notification(target))

# Обработчик для обновления существующей записи
@event.listens_for(ShadowQuestionInDb, 'after_update')
def after_update_listener(mapper, connection, target):
    asyncio.create_task(send_notification(target))

def custom_encoder(obj):
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%dT%H:%M:%S%z")
    elif isinstance(obj, UUID):
        return str(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

async def send_notification(target):
    user_uid = target.user_uid
    if user_uid in active_websockets:
        # Fetch all ShadowQuestionInDb for the given user_uid
        shadow_questions_in_db = await crud.users.get_shadow_questions(db=session, user_uid=user_uid)
        shadow_questions_dicts = [ShadowQuestion(**shadow_question_in_db.__dict__).model_dump() for shadow_question_in_db in shadow_questions_in_db]

        result_json = json.dumps(shadow_questions_dicts, default=custom_encoder, ensure_ascii=False)

        # Send the list to the websocket if it's active for the user
        print(result_json)

        websocket = active_websockets[user_uid]
        current_loop = asyncio.get_event_loop()
        current_loop.create_task(websocket.send_text(result_json))



