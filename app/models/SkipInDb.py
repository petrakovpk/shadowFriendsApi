from sqlalchemy import Column, TIMESTAMP, VARCHAR, UUID

from config import Base

class SkipInDb(Base):
    __tablename__ = 'skips'

    uuid = Column("uuid", UUID, primary_key=True, nullable=False)
    user_uid = Column("user_uid", VARCHAR, nullable=False)
    shadow_question_uuid = Column("shadow_question_uuid", UUID, nullable=False)
    created = Column("created", TIMESTAMP(timezone=True), nullable=False)

