"""init schema

Revision ID: c7e94e00e298
Revises: 
Create Date: 2025-08-12 10:59:17.360772

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7e94e00e298'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(length=64), nullable=False, unique=True),
    )

    op.create_table(
        'chats',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=128), nullable=False, unique=True),
        sa.Column('pinned_message_id', sa.Integer(), nullable=True),
    )

    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('is_system', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_messages_chat_id ON messages (chat_id)")

    op.create_table(
        'chat_members',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('chat_id', 'user_id', name='uq_chat_members_chat_user'),
    )

    op.create_foreign_key(
        'fk_chats_pinned_message_id',
        'chats', 'messages',
        ['pinned_message_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_chats_pinned_message_id', 'chats', type_='foreignkey')
    op.drop_table('chat_members')
    op.execute("DROP INDEX IF EXISTS ix_messages_chat_id")
    op.drop_table('messages')
    op.drop_table('chats')
    op.drop_table('users')
