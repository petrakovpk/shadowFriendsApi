from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import UserInDb, ShadowQuestionInDb, ShadowAnswerInDb
from schemas import UserCreate, UserUpdate

async def get_user(db: AsyncSession, user_uid: str) -> Optional[UserInDb]:
    result = await db.execute(select(UserInDb).filter(UserInDb.uid == user_uid))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: UserCreate) -> UserInDb:
    user_in_db = UserInDb(**user.__dict__)
    await db.add(user_in_db)
    await db.commit()
    await db.refresh(user_in_db)
    return user_in_db

async def update_user(db: AsyncSession, user: UserUpdate) -> UserInDb:
    user_in_db = await get_user(db=db, user_uid=user.uid)
    await user_in_db.update(user, commit=True, db=db)
    return user_in_db

async def get_recommended_shadow_questions(db: AsyncSession, user_uid: str) -> [ShadowQuestionInDb]:
    subquery = select(ShadowAnswerInDb.question_uuid).filter(ShadowAnswerInDb.user_uid == user_uid)
    result = await db.execute(select(ShadowQuestionInDb).filter(ShadowQuestionInDb.uuid.not_in(subquery)))
    return result.scalars().all()

async def get_shadow_questions(db: AsyncSession, user_uid: str) -> Optional[ShadowQuestionInDb]:
    result = await db.execute(select(ShadowQuestionInDb).filter(ShadowQuestionInDb.user_uid == user_uid))
    return result.scalars().all()
