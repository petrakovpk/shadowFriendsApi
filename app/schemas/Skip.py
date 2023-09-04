from pydantic import UUID4
from datetime import datetime
from config import SFBaseModel

class SkipBase(SFBaseModel):
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


