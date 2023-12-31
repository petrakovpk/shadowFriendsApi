from pydantic import UUID4
from datetime import datetime
from config import BaseModel
from typing import Optional


class ShadowAnswerBase(BaseModel):
    text: str
    upload_date: Optional[datetime]

class ShadowAnswerCreate(ShadowAnswerBase):
    uuid: UUID4
    created: datetime
    user_uid: str
    shadow_question_uuid: UUID4

class ShadowAnswerUpdate(ShadowAnswerBase):
    pass

class ShadowAnswer(ShadowAnswerBase):
    uuid: UUID4
    created: datetime
    user_uid: str
    shadow_question_uuid: UUID4

