from sqlalchemy import Column, TIMESTAMP, VARCHAR, UUID

from config import Base

class ShadowAnswerInDb(Base):
    __tablename__ = 'shadow_answers'

    uuid = Column("uuid", UUID, primary_key=True)
    text = Column("text", VARCHAR)
    shadow_question_uuid = Column("shadow_question_uuid", UUID)
    user_uid = Column("user_uid", VARCHAR, nullable=False)
    created = Column("created", TIMESTAMP(timezone=True), nullable=False)
    upload_date = Column("upload_date", TIMESTAMP(timezone=True), nullable=True)

