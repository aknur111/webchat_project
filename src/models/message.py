import datetime as dt
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Text, DateTime, Boolean, ForeignKey, func
from src.config.database import Base

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    chat: Mapped["Chat"] = relationship(
        "Chat", back_populates="messages", foreign_keys=[chat_id]
    )
    user: Mapped["User | None"] = relationship("User", back_populates="messages")
