from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    uid: str

class UserCreate(UserBase):
    created: datetime
    last_activity: datetime

class UserUpdate(UserBase):
    last_activity: datetime

class User(UserBase):
    created: datetime
    last_activity: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S%z")
        }


