from sqlalchemy import Column, TIMESTAMP, VARCHAR, UUID

from db import Base

class ShadowAnswerInDb(Base):
    __tablename__ = 'shadow_answers'

    uuid = Column("uuid", UUID, primary_key=True, nullable=False)
    text = Column("text", VARCHAR, nullable=True)
    created = Column("created", TIMESTAMP(timezone=True), nullable=False)
    upload_date = Column("upload_date", TIMESTAMP(timezone=True), nullable=True)
    user_uid = Column("user_uid", VARCHAR, nullable=False)
    shadow_question_uuid = Column("shadow_question_uuid", UUID, nullable=False)

