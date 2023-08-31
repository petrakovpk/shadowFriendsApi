from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import uuid4

from models import ShadowAnswerInDb
from schemas import ShadowAnswerCreate, ShadowAnswerUpdate

async def get_shadow_answer(db: AsyncSession, shadow_answer_uuid: uuid4) -> Optional[ShadowAnswerInDb]:
    stmt = select(ShadowAnswerInDb).where(ShadowAnswerInDb.uuid == shadow_answer_uuid)
    result = await db.execute(stmt)
    shadow_answer_in_db = result.scalar_one_or_none()
    return shadow_answer_in_db

async def create_shadow_answer(db: AsyncSession, shadow_answer: ShadowAnswerCreate) -> Optional[ShadowAnswerInDb]:
    user_in_db = ShadowAnswerInDb(**shadow_answer.__dict__)
    await db.add(user_in_db)
    await db.commit()
    await db.refresh(user_in_db)
    return user_in_db

async def update_shadow_answer(db: AsyncSession, shadow_answer_uuid: uuid4, shadow_answer: ShadowAnswerUpdate) -> Optional[ShadowAnswerInDb]:
    shadow_answer_in_db = await get_shadow_answer(db=db, shadow_answer_uuid=shadow_answer_uuid)
    await shadow_answer_in_db.update(model=shadow_answer, commit=True, db=db)
    return shadow_answer_in_db



