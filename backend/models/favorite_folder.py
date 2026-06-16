from datetime import datetime
from sqlalchemy import Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime, Integer, String
from models.news import Base


class FavoriteFolder(Base):
    __tablename__ = "favorite_folder"
    __table_args__ = (Index('idx_folder_user', 'user_id'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
