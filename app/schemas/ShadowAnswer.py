from pydantic import BaseModel, UUID4
from datetime import datetime

class ShadowAnswerBase(BaseModel):
    text: str
    status: str
    last_update: datetime

class ShadowAnswerCreate(ShadowAnswerBase):
    uuid: UUID4
    created: datetime
    user_uid: str
    question_uuid: UUID4

class ShadowAnswerUpdate(ShadowAnswerBase):
    pass

class ShadowAnswer(ShadowAnswerBase):
    uuid: UUID4
    created: datetime
    user_uid: str
    question_uuid: UUID4

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S%z")
        }




