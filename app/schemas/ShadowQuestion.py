from pydantic import BaseModel, UUID4
from datetime import datetime

class ShadowQuestionBase(BaseModel):
    text: str
    status: str
    last_update: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S%z"),
            UUID4: lambda v: str(v)
        }

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






