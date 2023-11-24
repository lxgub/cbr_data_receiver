"""
Project entrypoint
"""
import os.path
from os import system
from cbr_data_receiver import config_system_dir
from cbr_data_receiver.singletons import get_config
from cbr_data_receiver.worker import CbrWorker, Requester, PostgreSQLClient


def main():
    """
    Project entrypoint
    """
    config = get_config()
    db_client = PostgreSQLClient.get_client(conf=config.pgdb)
    requester = Requester(config.cbrf_api)
    while True:
        CbrWorker(config=config,
                  db_client=db_client,
                  requester=requester).start()


def run_migrations():
    """
    Runs alembic migrations
    """
    alembic_ini = os.path.join(config_system_dir(), "alembic.ini")
    system(f"alembic -c {alembic_ini} upgrade head")


def down_migration():
    """
    Rolls back one migration
    """
    alembic_ini: str = os.path.join(config_system_dir(), "alembic.ini")
    system(f"alembic -c '{alembic_ini}' downgrade -1")

