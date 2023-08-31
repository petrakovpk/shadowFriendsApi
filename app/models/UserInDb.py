from sqlalchemy import Column, TIMESTAMP, VARCHAR
from sqlalchemy.orm import Session

from config import Base
from schemas import UserUpdate

class UserInDb(Base):
    __tablename__ = 'users'

    uid = Column("uid", VARCHAR, primary_key=True)
    created = Column("created", TIMESTAMP(timezone=True), nullable=False)
    last_activity = Column("last_activity", TIMESTAMP(timezone=True), nullable=False)

    def update(self, user: UserUpdate, commit: bool, db: Session):
        for field, value in user.dict(exclude_unset=True).items():
            setattr(self, field, value)

        if commit:
            db.merge(self)
            db.commit()
            db.refresh(self)
