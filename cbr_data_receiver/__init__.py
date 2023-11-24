from sys import prefix
import os.path

__projectname__ = "cbr_data_receiver"

__verison__ = "0.0.1"


def config_system_dir():
    """Path to configuration files.
    """
    return os.path.join(prefix, "etc", __projectname__)
