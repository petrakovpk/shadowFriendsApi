import json
from sqlalchemy import Column, TIMESTAMP, VARCHAR, UUID
from sqlalchemy.orm import Session

from db import Base
from schemas import ShadowQuestionUpdate


class ShadowQuestionInDb(Base):
    __tablename__ = 'shadow_questions'

    uuid = Column("uuid", UUID, primary_key=True, nullable=False)
    text = Column("text", VARCHAR, nullable=True)
    status = Column("status", VARCHAR, nullable=False)
    created = Column("created", TIMESTAMP(timezone=True), nullable=False)
    upload_date = Column("upload_date", TIMESTAMP(timezone=True), nullable=False)
    user_uid = Column("user_uid", VARCHAR, nullable=False)

