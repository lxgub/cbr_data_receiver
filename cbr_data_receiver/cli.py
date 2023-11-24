import os
import os.path
import shutil
from os import environ

from cbr_data_receiver.__init__ import config_system_dir
from cbr_data_receiver.logger import get_logger


def set_configuration():
    """
    Copies the configuration defined in the "CONFIG" variable.
    """
    configsystemdir = config_system_dir()
    configsubdir = environ.get("CONFIG", "local")
    get_logger().info(f"Configuration \"{configsubdir}\" was selected.")
    copy_dir_content(
        os.path.join(configsystemdir, "config", configsubdir),
        configsystemdir
    )


def copy_dir_content(dir_from, dir_to):
    """Copies the contents of one directory to another.
      Both directories must exist.
    """
    for f in os.listdir(dir_from):
        file_from = os.path.join(dir_from, f)
        if os.path.isfile(file_from):
            remove_file(os.path.join(dir_to, f))
            shutil.copy(file_from, dir_to)
        if os.path.isdir(file_from):
            remove_file(os.path.join(dir_to, f))
            shutil.copytree(file_from, os.path.join(dir_to, f))


def remove_file(filename):
    """Deletes a file or directory if it exists.
    """
    try:
        if os.path.isfile(filename):
            os.remove(filename)
        elif os.path.isdir(filename):
            shutil.rmtree(filename)
    except Exception:
        pass
