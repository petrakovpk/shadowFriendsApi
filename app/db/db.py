from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase

from config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_SERVER, POSTGRES_PORT, POSTGRES_DB

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
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    async def update(self, model: BaseModel, commit: bool, db: Session):
        for field, value in model.model_dump().items():
            setattr(self, field, value)

        if commit:
            await db.merge(self)
            await db.commit()
            await db.refresh(self)