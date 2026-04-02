"""merge_heads

Revision ID: 6da6c0eb2b85
Revises: 263e0964e5b8, 460f4f7d1098
Create Date: 2026-04-02 11:11:38.837035

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6da6c0eb2b85'
down_revision: Union[str, Sequence[str], None] = ('263e0964e5b8', '460f4f7d1098')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
