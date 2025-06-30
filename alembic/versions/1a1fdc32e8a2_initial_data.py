"""Initial data

Revision ID: 1a1fdc32e8a2
Create Date: 2024-02-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geography

# revision identifiers, used by Alembic.
revision = '1a1fdc32e8a2'
down_revision = '000_create_tables'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Создаем здания
    op.execute("""
        INSERT INTO buildings (address, location) VALUES
        ('г. Москва, ул. Ленина 1', ST_SetSRID(ST_MakePoint(37.6173, 55.7558), 4326)),
        ('г. Москва, ул. Тверская 2', ST_SetSRID(ST_MakePoint(37.6067, 55.7648), 4326));
    """)

    # Создаем виды деятельности
    op.execute("""
        INSERT INTO activities (id, name, parent_id, level) VALUES
        (1, 'Еда', NULL, 1),
        (2, 'Мясная продукция', 1, 2),
        (3, 'Молочная продукция', 1, 2),
        (4, 'Автомобили', NULL, 1),
        (5, 'Грузовые', 4, 2),
        (6, 'Легковые', 4, 2),
        (7, 'Запчасти', 6, 3),
        (8, 'Аксессуары', 6, 3);
    """)

    # Создаем организации
    op.execute("""
        INSERT INTO organizations (name, building_id) VALUES
        ('ООО "Рога и Копыта"', 1),
        ('ЗАО "АвтоМир"', 2);
    """)

    # Создаем телефоны
    op.execute("""
        INSERT INTO phones (number, organization_id) VALUES
        ('2-222-222', 1),
        ('3-333-333', 1),
        ('8-923-666-13-13', 1),
        ('4-444-444', 2),
        ('5-555-555', 2);
    """)

    # Связываем организации с видами деятельности
    op.execute("""
        INSERT INTO organization_activity (organization_id, activity_id) VALUES
        (1, 2),
        (1, 3),
        (2, 6),
        (2, 7),
        (2, 8);
    """)

def downgrade() -> None:
    op.execute("DELETE FROM organization_activity;")
    op.execute("DELETE FROM phones;")
    op.execute("DELETE FROM organizations;")
    op.execute("DELETE FROM activities;")
    op.execute("DELETE FROM buildings;")
