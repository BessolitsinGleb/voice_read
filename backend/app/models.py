from sqlalchemy.orm import Mapped, mapped_column
from .database import Base
from datetime import datetime

class Users(Base):

    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=True)
    email_verified: Mapped[bool] = mapped_column(default= False)
    password: Mapped[str] = mapped_column()

class EmailCode(Base):
    __tablename__ = "email_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False)
    code: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column()