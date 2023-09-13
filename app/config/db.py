import os
import datetime
import json
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Создаем асинхронный engine для подключения к базе данных PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем асинхронную сессию для работы с базой данных
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

session = AsyncSessionLocal()

async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

class Base(DeclarativeBase):

    def to_json(self):
        def custom_encoder(o):
            if isinstance(o, datetime.datetime):
                return o.isoformat()
            if hasattr(o, '__dict__'):
                return o.__dict__
            raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

        return json.dumps(self, default=custom_encoder, sort_keys=True, indent=4)
    async def update(self, model: BaseModel, commit: bool, db: Session):
        for field, value in model.model_dump().items():
            setattr(self, field, value)

        if commit:
            await db.merge(self)
            await db.commit()
            await db.refresh(self)


class SFBaseModel(BaseModel):
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: (v.replace(microsecond=int(v.microsecond/10000)*10000)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }