import logging
import uvicorn

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
from fastapi.testclient import TestClient

from api import router

app = FastAPI()
app.include_router(router, prefix="/api", tags=["api"])

origins = [
    "http://194.67.103.134",
    "http://194.67.103.134:32782",
    "http://www.dota2-lab.ru",
    "http://dota2-lab.ru",
    "https://www.dota2-lab.ru",
    "https://dota2-lab.ru",
    "http://127.0.0.1:3000",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

def start():
	"""Launched with `poetry run start` at root level"""
	uvicorn.run("app.main:app", host="0.0.0.0", port=7070, reload=True)

@app.websocket("/ws")
async def websocket(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"msg": "Hello WebSocket"})
    await websocket.close()
