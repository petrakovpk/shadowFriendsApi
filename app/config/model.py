from datetime import datetime
from pydantic import BaseModel
from uuid import UUID

class CustomBaseModel(BaseModel):
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: (v.replace(microsecond=int(v.microsecond/10000)*10000)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            UUID: lambda v: str(v)
        }