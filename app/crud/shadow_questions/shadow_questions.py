from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from uuid import uuid4
from models import ShadowQuestionInDb, ShadowAnswerInDb
from schemas import ShadowQuestionCreate, ShadowQuestionUpdate

async def get_shadow_question(db: AsyncSession, shadow_question_uuid: uuid4) -> Optional[ShadowQuestionInDb]:
    stmt = select(ShadowQuestionInDb).where(ShadowQuestionInDb.uuid == shadow_question_uuid)
    result = await db.execute(stmt)
    shadow_questions_in_db = result.scalar_one_or_none()
    return shadow_questions_in_db


async def create_shadow_question(db: AsyncSession, shadow_question: ShadowQuestionCreate) -> Optional[ShadowQuestionInDb]:
    shadow_questions_in_db = ShadowQuestionInDb(**shadow_question.__dict__)
    db.add(shadow_questions_in_db)
    await db.commit()
    await db.refresh(shadow_questions_in_db)
    return shadow_questions_in_db

async def get_shadow_answers(db: AsyncSession, shadow_question_uuid: uuid4) -> [ShadowAnswerInDb]:
    stmt = select(ShadowAnswerInDb).where(ShadowAnswerInDb.question_uuid == shadow_question_uuid)
    result = await db.execute(stmt)
    shadow_questions_in_db = result.scalars().all()
    return shadow_questions_in_db


async def update_shadow_question(db: AsyncSession, shadow_question_uuid: uuid4, shadow_question: ShadowQuestionUpdate) -> Optional[ShadowQuestionInDb]:
    shadow_question_in_db = await get_shadow_question(db=db, shadow_question_uuid=shadow_question_uuid)
    await shadow_question_in_db.update(shadow_question, commit=True, db=db)
    return shadow_question_in_db