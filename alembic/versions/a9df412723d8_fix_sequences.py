"""fix_sequences

Revision ID: a9df412723d8
Revises: 1a1fdc32e8a2
Create Date: 2025-06-30 06:29:23.598270

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a9df412723d8"
down_revision: Union[str, None] = "1a1fdc32e8a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Исправляем последовательности для автоинкремента ID
    # Устанавливаем следующее значение больше максимального существующего ID
    op.execute(
        "SELECT setval('activities_id_seq', "
        "(SELECT COALESCE(MAX(id), 0) + 1 FROM activities))"
    )
    op.execute(
        "SELECT setval('organizations_id_seq', "
        "(SELECT COALESCE(MAX(id), 0) + 1 FROM organizations))"
    )
    op.execute(
        "SELECT setval('buildings_id_seq', "
        "(SELECT COALESCE(MAX(id), 0) + 1 FROM buildings))"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # В downgrade ничего не делаем, так как это исправление не нужно откатывать
    pass
