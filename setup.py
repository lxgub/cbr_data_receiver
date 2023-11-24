#!/usr/bin/env python3

import io
import os
import shutil
import sys
from shutil import rmtree

from setuptools import Command, find_packages, setup

from cbr_data_receiver import __projectname__, __verison__, config_system_dir
from cbr_data_receiver.cli import set_configuration

NAME = __projectname__
DESCRIPTION = 'CBRF'
URL = 'http://example.com'
EMAIL = ''
AUTHOR = 'lxgub'
REQUIRES_PYTHON = '>=3.8.0'
VERSION = __verison__

REQUIRED = [
    'MarkupSafe==2.0.0',
    'alembic==1.7.7',
    'python-json-logger>=0.1.9',
    'pyyaml>=3.13',
    'xmltodict',
    'psycopg2-binary==2.8.6',
    'sqlalchemy>=1.2.12',
    'pytest',
    'tenacity==8.0.1',
    'requests',
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    with open(os.path.join(here, NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds...')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution...')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine...')
        os.system('twine upload dist/*')

        self.status('Pushing git tags...')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

        sys.exit()


# Setup parameters:
setupparams = dict(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    entry_points={
        'console_scripts': [
            f'{NAME}={NAME}.run:main',
            f"{NAME}_setconfiguration={NAME}.cli:set_configuration",
            f"{NAME}_runmigrations = {NAME}.run:run_migrations",
            f"{NAME}_downmigration = {NAME}.run:down_migration",
        ]
    },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=False,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)


def add_config(configfilename, text=None, force=True):
    destinationdir = os.path.join(config_system_dir())
    filepath = configfilename
    if force or not os.path.exists(os.path.join(destinationdir, configfilename)):
        try:
            os.makedirs(destinationdir, exist_ok=True)
            if text is not None:
                with open(os.path.join(destinationdir, configfilename), "w") as file_:
                    file_.write(text)
            else:
                shutil.copy(filepath, destinationdir)
        except PermissionError:
            pass


def add_dir(directory):
    configsystemdir = config_system_dir()
    destination = os.path.join(configsystemdir, directory)
    try:
        if os.path.exists(destination):
            shutil.rmtree(destination)
        shutil.copytree(directory, destination)
    except PermissionError:
        pass


# Install all configurations and select default:
add_dir("config")
add_dir("alembic")
add_config("alembic.ini")
set_configuration()

# Where the magic happens:
setup(**setupparams)
