from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from models import UserInDb, ShadowQuestionInDb, ShadowAnswerInDb
from schemas import UserCreate, UserUpdate

async def get_user(db: AsyncSession, user_uid: str) -> Optional[UserInDb]:
    result = await db.execute(select(UserInDb).filter(UserInDb.uid == user_uid))
    return result.scalar_one_or_none()

async def get_users(db: AsyncSession) -> List[UserInDb]:
    stms = select(UserInDb)
    result = await db.execute(stms)
    users_in_db = result.scalars().all()
    return users_in_db

async def create_user(db: AsyncSession, user: UserCreate) -> UserInDb:
    user_in_db = UserInDb(**user.__dict__)
    db.add(user_in_db)
    await db.commit()
    await db.refresh(user_in_db)
    return user_in_db

async def update_user(db: AsyncSession, user: UserUpdate) -> UserInDb:
    user_in_db = await get_user(db=db, user_uid=user.uid)
    await user_in_db.update(model=user, commit=True, db=db)
    return user_in_db

async def get_recommended_shadow_questions(db: AsyncSession, user_uid: str) -> List[ShadowQuestionInDb]:
    subquery = select(ShadowAnswerInDb.shadow_question_uuid).filter(ShadowAnswerInDb.user_uid == user_uid)
    stms = select(ShadowQuestionInDb).filter(ShadowQuestionInDb.uuid.not_in(subquery)).filter(ShadowQuestionInDb.user_uid!=user_uid)
    result = await db.execute(stms)
    shadow_questions_in_db = result.scalars().all()
    return shadow_questions_in_db

async def get_shadow_questions(db: AsyncSession, user_uid: str) -> List[ShadowQuestionInDb]:
    stms = select(ShadowQuestionInDb).filter(ShadowQuestionInDb.user_uid == user_uid)
    result = await db.execute(stms)
    shadow_questions_in_db = result.scalars().all()
    return shadow_questions_in_db

async def get_shadow_answers(db: AsyncSession, user_uid: str) -> List[ShadowAnswerInDb]:
    stms = select(ShadowAnswerInDb).filter(ShadowAnswerInDb.user_uid == user_uid)
    result = await db.execute(stms)
    shadow_answers_in_db = result.scalars().all()
    return shadow_answers_in_db
