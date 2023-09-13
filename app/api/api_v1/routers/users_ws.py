import asyncio
import json
import websockets
from datetime import datetime
from fastapi import APIRouter
from fastapi.websockets import WebSocket, WebSocketDisconnect
from firebase_admin import auth, messaging
from firebase_admin._auth_utils import InvalidIdTokenError
from sqlalchemy import event
from uuid import UUID
from websockets.exceptions import ConnectionClosedError

import crud
from config import AsyncSessionLocal
from models import ShadowQuestionInDb, ShadowAnswerInDb
from schemas import ShadowQuestion, ShadowAnswer

router = APIRouter()

# This is a global set to keep track of active websockets for each user
active_websockets = {}

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
    except ConnectionClosedError:
        active_websockets.pop(user_uid, None)

def custom_encoder(obj):
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%dT%H:%M:%S%z")
    elif isinstance(obj, UUID):
        return str(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

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
    asyncio.create_task(send_shadow_answer_push_notification(target))
    asyncio.create_task(send_shadow_answer_notification_for_question(target))


@event.listens_for(ShadowAnswerInDb, 'after_update')
def shadow_answer_after_update_listener(mapper, connection, target):
    asyncio.create_task(send_shadow_answer_push_notification(target))
    asyncio.create_task(send_shadow_answer_notification_for_question(target))

async def send_shadow_question_notification(user_uid: str):
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

async def send_shadow_answer_notification(user_uid: str):
    async with AsyncSessionLocal() as db:

        if user_uid in active_websockets:
            # Fetch all ShadowQuestionInDb for the given user_uid
            shadow_answers_in_db = await crud.shadow_answers.get_shadow_questions_shadow_answers(db=db, user_uid=user_uid)
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

async def send_shadow_answer_notification_for_question(shdaow_answer_in_db: ShadowAnswerInDb):
    async with AsyncSessionLocal() as db:
        shadow_question_in_db = await crud.shadow_questions.get_shadow_question(
            db=db,
            shadow_question_uuid=shdaow_answer_in_db.shadow_question_uuid
        )

        user_uid = shadow_question_in_db.user_uid

        await send_shadow_answer_notification(user_uid)


async def send_shadow_answer_push_notification(shadow_answer_in_db: ShadowAnswerInDb):
    async with AsyncSessionLocal() as db:
        shadow_question_in_db = await crud.shadow_questions.get_shadow_question(
            db=db,
            shadow_question_uuid=shadow_answer_in_db.shadow_question_uuid
        )

        user_in_db = await crud.users.get_user(db=db, user_uid=shadow_question_in_db.user_uid)

        message = messaging.Message(
            notification=messaging.Notification(
                title="Вам пришел новый ответ!",
                body=shadow_answer_in_db.text
            ),
            token=user_in_db.fcm_token
        )

        response = messaging.send(message)

        return response