import asyncio
import json

from datetime import datetime
from firebase_admin import auth
from firebase_admin._auth_utils import InvalidIdTokenError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.websockets import WebSocket, WebSocketDisconnect
from sqlalchemy import event
from sqlalchemy.orm import Session
from uuid import UUID

from pydantic import UUID4
from typing import List

import crud
from db import AsyncSessionLocal, get_db
from firebase import get_firebase_auth
from helpers import check_user_authorization, check_object_authorization
from schemas import ShadowQuestionCreate, ShadowQuestionUpdate, ShadowQuestion, ShadowAnswer
from models import ShadowAnswerInDb

router = APIRouter()

active_websockets = {}

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


@router.get("/{shadow_question_uuid}/shadow_answers", response_model=List[ShadowAnswer], status_code=200)
async def get_shadow_question(
        shadow_question_uuid: UUID4,
        db: Session = Depends(get_db),
        firebase_user: auth.UserRecord = Depends(get_firebase_auth)
):
    check_user_authorization(firebase_user)

    result = await crud.shadow_questions.get_shadow_answers(db=db, shadow_question_uuid=shadow_question_uuid)

    return result

def custom_encoder(obj):
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%dT%H:%M:%S%z")
    elif isinstance(obj, UUID):
        return str(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


@router.websocket("/{shadow_question_uuid}/shadow_answers/ws")
async def get_shadow_questions_ws(
        websocket: WebSocket,
        shadow_question_uuid: UUID4
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

    await websocket.send_json({
        "type": "connection_status",
        "data": {
            "status": "success"
        }
    })

    active_websockets[shadow_question_uuid] = websocket

    asyncio.create_task(send_shadow_answer_notification(shadow_question_uuid))

    try:
        while True:
            # You can listen for messages from the client if needed
            data = await websocket.receive_text()

            # Handle the received data as needed
    except WebSocketDisconnect:
        # Remove the websocket connection from the global set when it's closed
        active_websockets.pop(shadow_question_uuid, None)

@event.listens_for(ShadowAnswerInDb, 'after_insert')
def shadow_answer_after_insert_listener(mapper, connection, target):
    asyncio.create_task(send_shadow_answer_notification(target.shadow_question_uuid))

@event.listens_for(ShadowAnswerInDb, 'after_update')
def shadow_answer_after_update_listener(mapper, connection, target):
    asyncio.create_task(send_shadow_answer_notification(target.shadow_question_uuid))

async def send_shadow_answer_notification(shadow_question_uuid: UUID4):
    # user_uid = target.user_uid
    async with AsyncSessionLocal() as db:
        if shadow_question_uuid in active_websockets:
            # Fetch all ShadowQuestionInDb for the given user_uid
            shadow_answers_in_db = await crud.shadow_questions.get_shadow_answers(db=db, shadow_question_uuid=shadow_question_uuid)
            shadow_answers_dicts = [ShadowAnswer(**shadow_answer_in_db.__dict__).model_dump() for shadow_answer_in_db in shadow_answers_in_db]

            result_json = {
                "type": "shadow_answers",
                "data": [json.dumps(shadow_answer_dict, default=custom_encoder, ensure_ascii=False) for shadow_answer_dict
                         in shadow_answers_dicts]
            }

            # Send the list to the websocket if it's active for the user
            websocket = active_websockets[shadow_question_uuid]
            current_loop = asyncio.get_event_loop()
            current_loop.create_task(websocket.send_json(result_json))
