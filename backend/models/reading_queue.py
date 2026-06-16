from datetime import datetime
from sqlalchemy import Index, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime, Integer
from models.news import Base


class ReadingQueue(Base):
    __tablename__ = "reading_queue"
    __table_args__ = (
        UniqueConstraint('user_id', 'news_id', name='uq_user_news_queue'),
        Index('idx_queue_user', 'user_id'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey("news.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
