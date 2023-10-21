from pydantic import UUID4
from datetime import datetime
from config import BaseModel

class SkipBase(BaseModel):
    uuid: UUID4
    created: datetime
    user_uid: str
    shadow_question_uuid: UUID4

class SkipCreate(SkipBase):
    pass

class Skip(SkipBase):
    pass

