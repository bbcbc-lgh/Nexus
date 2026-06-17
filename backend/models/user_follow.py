from datetime import datetime
from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime, Integer, String
from models.news import Base


class UserFollow(Base):
    __tablename__ = "user_follow"
    __table_args__ = (
        UniqueConstraint("user_id", "follow_type", "follow_value", name="uk_user_follow_value"),
        Index("idx_user_follow_type", "user_id", "follow_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    follow_type: Mapped[str] = mapped_column(String(20), nullable=False)
    follow_value: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
