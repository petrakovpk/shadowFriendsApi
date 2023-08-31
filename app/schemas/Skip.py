from pydantic import BaseModel, UUID4
from datetime import datetime

class SkipBase(BaseModel):
    uuid: UUID4
    created: datetime
    user_uid: str
    shadow_question_uuid: UUID4

class SkipCreate(SkipBase):
    pass

class Skip(SkipBase):

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S%z")
        }


