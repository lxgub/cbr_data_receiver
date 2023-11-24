"""
Project configuration module
"""
import yaml


class Config:
    """
    Contains main project settings
    """
    raw = None
    loglevel = None

    def __init__(self, config_file, **params):
        self.loglevel = params.get("loglevel", 'INFO')

        with open(config_file) as file:
            self.raw = yaml.safe_load(file)

        self.pgdb = self.raw["postgres"]
        self.cbrf_api = self.raw["cbrf_api"]
        self.waiting_time = self.raw["waiting_time"]
