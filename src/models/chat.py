# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from sqlalchemy import Integer, String, ForeignKey
# from src.config.database import Base
#
# class Chat(Base):
#     __tablename__ = "chats"
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
#
#     pinned_message_id: Mapped[int | None] = mapped_column(
#         ForeignKey("messages.id", ondelete="SET NULL"), nullable=True
#     )
#
#     messages: Mapped[list["Message"]] = relationship(
#         "Message",
#         back_populates="chat",
#         cascade="all, delete-orphan",
#         foreign_keys="Message.chat_id",
#         passive_deletes=True,
#     )
#
#     pinned_message: Mapped["Message | None"] = relationship(
#         "Message",
#         foreign_keys="Chat.pinned_message_id",
#         uselist=False,
#         post_update=True,
#     )
#
#     members: Mapped[list["ChatMember"]] = relationship(
#         "ChatMember",
#         back_populates="chat",
#         cascade="all, delete-orphan",
#         passive_deletes=True,
#     )

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint
from src.config.database import Base

class Chat(Base):
    __tablename__ = "chats"
    __table_args__ = (
        UniqueConstraint("join_code", name="uq_chats_join_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)

    join_code: Mapped[str] = mapped_column(String(16), nullable=False, unique=True)

    pinned_message_id: Mapped[int | None] = mapped_column(
        ForeignKey("messages.id", ondelete="SET NULL"), nullable=True
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan",
        foreign_keys="Message.chat_id",
        passive_deletes=True,
    )
    pinned_message: Mapped["Message | None"] = relationship(
        "Message", foreign_keys="Chat.pinned_message_id", uselist=False, post_update=True
    )
    members: Mapped[list["ChatMember"]] = relationship(
        "ChatMember", back_populates="chat", cascade="all, delete-orphan", passive_deletes=True
    )
