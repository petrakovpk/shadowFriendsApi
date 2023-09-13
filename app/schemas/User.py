from datetime import datetime
from typing import Optional

from config import SFBaseModel

class UserBase(SFBaseModel):
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


