import os.path
import sys
from argparse import ArgumentParser

from . import config_system_dir
from .config import Config as BaseConfig


class Singleton(type):
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def parse_args():
    parser = ArgumentParser("CHANGE ME!")

    parser.add_argument(
        "-c", "--config", type=str, required=False,
        help="Config file with the service parameters.")
    parser.add_argument(
        "-l", "--loglevel", type=str, required=False,
        default="INFO",
        help="logLevel from logging. May be set NOTSET/DEBUG/INFO/WARNING/ERROR/CRITICAL")
    parser.add_argument(
        "-b", "--bind", type=str, required=False,
        help="The service host.")
    parser.add_argument(
        "-p", "--port", type=int, required=False,
        help="The service port.")
    params = parser.parse_args(sys.argv[1:]).__dict__
    return {k: v for k, v in params.items() if v is not None}


class Config(BaseConfig, metaclass=Singleton):
    def __init__(self):
        params = parse_args()
        config_file = params.get("config")
        if not config_file:
            config_file = os.path.join(config_system_dir(), "access.yaml")
        BaseConfig.__init__(self, config_file, **params)


class ConfigForMigrations(BaseConfig, metaclass=Singleton):
    def __init__(self):
        config_file = os.path.join(config_system_dir(), "access.yaml")
        BaseConfig.__init__(self, config_file=config_file, alembic=True)


def get_config():
    return Config()
