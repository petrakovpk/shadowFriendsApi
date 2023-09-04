from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import uuid4

from models import ShadowAnswerInDb, ShadowQuestionInDb
from schemas import ShadowAnswerCreate, ShadowAnswerUpdate, ShadowQuestion

async def get_shadow_answer(db: AsyncSession, shadow_answer_uuid: uuid4) -> Optional[ShadowAnswerInDb]:
    stmt = select(ShadowAnswerInDb).where(ShadowAnswerInDb.uuid == shadow_answer_uuid)
    result = await db.execute(stmt)
    shadow_answer_in_db = result.scalar_one_or_none()
    return shadow_answer_in_db

async def get_shadow_answers(db: AsyncSession, user_uid: str) -> List[ShadowAnswerInDb]:
    stms = select(ShadowQuestionInDb).where(ShadowQuestionInDb.user_uid == user_uid)
    result = await db.execute(stms)
    shadow_questions_in_db = result.scalars().all()
    shadow_question_in_db_uuids = [q.uuid for q in shadow_questions_in_db]  # извлекаем UUIDs из списка вопросов
    stmt = select(ShadowAnswerInDb).where(ShadowAnswerInDb.question_uuid.in_(shadow_question_in_db_uuids))  # Используем in_ для поиска по множественным UUIDs
    result = await db.execute(stmt)
    shadow_answers_in_db = result.scalars().all()  # получаем все соответствующие записи
    return shadow_answers_in_db

async def create_shadow_answer(db: AsyncSession, shadow_answer: ShadowAnswerCreate) -> Optional[ShadowAnswerInDb]:
    user_in_db = ShadowAnswerInDb(**shadow_answer.__dict__)
    db.add(user_in_db)
    await db.commit()
    await db.refresh(user_in_db)
    return user_in_db

async def update_shadow_answer(db: AsyncSession, shadow_answer_uuid: uuid4, shadow_answer: ShadowAnswerUpdate) -> Optional[ShadowAnswerInDb]:
    shadow_answer_in_db = await get_shadow_answer(db=db, shadow_answer_uuid=shadow_answer_uuid)
    await shadow_answer_in_db.update(model=shadow_answer, commit=True, db=db)
    return shadow_answer_in_db



