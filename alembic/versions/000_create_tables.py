"""Create tables

Revision ID: 000_create_tables
Revises: 
Create Date: 2025-06-30 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geography

# revision identifiers, used by Alembic.
revision: str = '000_create_tables'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Создаем таблицу buildings
    op.create_table('buildings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('location', Geography(geometry_type='POINT', srid=4326), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_buildings_id'), 'buildings', ['id'], unique=False)
    op.create_index(op.f('ix_buildings_address'), 'buildings', ['address'], unique=False)

    # Создаем таблицу activities
    op.create_table('activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['activities.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activities_id'), 'activities', ['id'], unique=False)
    op.create_index(op.f('ix_activities_name'), 'activities', ['name'], unique=False)

    # Создаем таблицу organizations
    op.create_table('organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('building_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['building_id'], ['buildings.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=False)

    # Создаем таблицу phones
    op.create_table('phones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('number', sa.String(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_phones_id'), 'phones', ['id'], unique=False)

    # Создаем таблицу связи organization_activity
    op.create_table('organization_activity',
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('activity_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('organization_activity')
    op.drop_index(op.f('ix_phones_id'), table_name='phones')
    op.drop_table('phones')
    op.drop_index(op.f('ix_organizations_name'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_id'), table_name='organizations')
    op.drop_table('organizations')
    op.drop_index(op.f('ix_activities_name'), table_name='activities')
    op.drop_index(op.f('ix_activities_id'), table_name='activities')
    op.drop_table('activities')
    op.drop_index(op.f('ix_buildings_address'), table_name='buildings')
    op.drop_index(op.f('ix_buildings_id'), table_name='buildings')
    op.drop_table('buildings')
