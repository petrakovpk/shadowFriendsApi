import json
import datetime
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

    def to_json(self):
        def custom_encoder(o):
            if isinstance(o, datetime.datetime):
                return o.isoformat()
            if hasattr(o, '__dict__'):
                return o.__dict__
            raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

        return json.dumps(self, default=custom_encoder, sort_keys=True, indent=4)

    async def update(self, shadow_question: ShadowQuestionUpdate, commit: bool, db: Session):
        for field, value in shadow_question.dict(exclude_unset=True).items():
            setattr(self, field, value)

        if commit:
            await db.merge(self)
            await db.commit()
            await db.refresh(self)
