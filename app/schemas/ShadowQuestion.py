from pydantic import UUID4
from datetime import datetime
from config import SFBaseModel
from typing import Optional

class ShadowQuestionBase(SFBaseModel):
    text: str
    status: str
    upload_date: Optional[datetime]

class ShadowQuestionCreate(ShadowQuestionBase):
    uuid: UUID4
    created: datetime
    user_uid: str

class ShadowQuestionUpdate(ShadowQuestionBase):
    pass

class ShadowQuestion(ShadowQuestionBase):
    uuid: UUID4
    created: datetime
    user_uid: str







