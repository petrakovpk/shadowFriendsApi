from sqlalchemy import Column, TIMESTAMP, VARCHAR
from sqlalchemy.orm import Session

from config import Base
from schemas import UserUpdate

class UserInDb(Base):
    __tablename__ = 'users'

    uid = Column("uid", VARCHAR, primary_key=True)
    created = Column("created", TIMESTAMP(timezone=True), nullable=False)
    last_activity = Column("last_activity", TIMESTAMP(timezone=True), nullable=False)