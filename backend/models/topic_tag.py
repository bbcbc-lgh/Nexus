from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class TopicTag(Base):
    __tablename__ = "topic_tag"
    id:    Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name:  Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    slug:  Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#C8860A")


class NewsTopicTag(Base):
    __tablename__ = "news_topic_tag"
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id", ondelete="CASCADE"), primary_key=True)
    tag_id:  Mapped[int] = mapped_column(ForeignKey("topic_tag.id", ondelete="CASCADE"), primary_key=True)
