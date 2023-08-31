from sqlalchemy import Column, TIMESTAMP, VARCHAR, UUID
from sqlalchemy.orm import Session

from config import Base
from schemas import ShadowAnswerUpdate

class ShadowAnswerInDb(Base):
    __tablename__ = 'shadow_answers'

    uuid = Column("uuid", UUID, primary_key=True)
    text = Column("text", VARCHAR)
    status = Column("status", VARCHAR, nullable=False)
    created = Column("created", TIMESTAMP(timezone=True), nullable=False)
    last_update = Column("last_update", TIMESTAMP(timezone=True), nullable=False)
    user_uid = Column("user_uid", VARCHAR, nullable=False)
    question_uuid = Column("question_uuid", UUID)

    def update(self, user: ShadowAnswerUpdate, commit: bool, db: Session):
        for field, value in user.dict(exclude_unset=True).items():
            setattr(self, field, value)

        if commit:
            db.merge(self)
            db.commit()
            db.refresh(self)
