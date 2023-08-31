from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from models import SkipInDb
from schemas import SkipCreate

async def get_skip(db: AsyncSession, skip_uuid: uuid4) -> Optional[SkipInDb]:
    query = await db.query(SkipInDb).filter(SkipInDb.uuid == skip_uuid)
    skip_in_db = query.scalar_one_or_none()
    return skip_in_db

async def create_skip(db: AsyncSession, skip: SkipCreate) -> Optional[SkipInDb]:
    skip_in_db = SkipInDb(**skip.__dict__)
    await db.add(skip_in_db)
    await db.commit()
    await db.refresh(skip_in_db)
    return skip_in_db



