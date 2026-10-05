"""baseline

Revision ID: f496d704f4ef
Revises: 
Create Date: 2026-10-05 16:25:52.911983

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = 'f496d704f4ef'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
