"""init_revision

Revision ID: fda2983f0d49
Revises: 
Create Date: 2022-06-12 09:18:57.413133

"""
import sqlalchemy as sa

from cbr_data_receiver.singletons import ConfigForMigrations
from cbr_data_receiver.models import metadata
from cbr_data_receiver.models import schema_name

# revision identifiers, used by Alembic.
revision = 'fda2983f0d45'
down_revision = None
branch_labels = None
depends_on = None

config = ConfigForMigrations()
user = config.pgdb['user']
password = config.pgdb['password']
host = config.pgdb['host']
port = config.pgdb['port']
dbname = config.pgdb['dbname']
engine = sa.create_engine(
    f'''postgresql://{user}:{password}@{host}:{port}/{dbname}''')


def upgrade():
    engine.execute(sa.schema.CreateSchema(schema_name))
    metadata.create_all(engine)


def downgrade():
    metadata.drop_all(engine)
    engine.execute(sa.schema.DropSchema(schema_name))
