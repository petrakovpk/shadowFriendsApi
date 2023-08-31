import json
from sqlalchemy import Column, TIMESTAMP, VARCHAR, UUID
from sqlalchemy.orm import Session

from config import Base
from schemas import ShadowQuestionUpdate


class ShadowQuestionInDb(Base):
    __tablename__ = 'shadow_questions'

    uuid = Column("uuid", UUID, primary_key=True)
    text = Column("text", VARCHAR)
    status = Column("status", VARCHAR, nullable=False)
    created = Column("created", TIMESTAMP(timezone=True), nullable=False)
    last_update = Column("last_update", TIMESTAMP(timezone=True), nullable=False)
    user_uid = Column("user_uid", VARCHAR, nullable=False)
