from datetime import datetime
from typing import Optional

from config import CustomBaseModel

class UserBase(CustomBaseModel):
    uid: str
    fcm_token: Optional[str]

class UserCreate(UserBase):
    created: datetime = datetime.now()
    last_activity: datetime = datetime.now()

class UserUpdate(UserBase):
    last_activity: datetime = datetime.now()

class User(UserBase):
    created: datetime
    last_activity: datetime


