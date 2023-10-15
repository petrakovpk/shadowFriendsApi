from sqlalchemy import Column, TIMESTAMP, VARCHAR

from config import Base

class UserInDb(Base):
    __tablename__ = 'users'

    uid = Column("uid", VARCHAR, primary_key=True, nullable=False)
    fcm_token = Column("fcm_token", VARCHAR, nullable=True)
    created = Column("created", TIMESTAMP(timezone=True), nullable=False)
    last_activity = Column("last_activity", TIMESTAMP(timezone=True), nullable=False)
