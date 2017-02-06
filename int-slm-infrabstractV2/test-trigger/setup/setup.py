# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# configure plugin name here
PLUGIN_NAME = "son-mano-example-plugin-1"

# generate a name without dashes
PLUGIN_NAME_CLEAR = "son_mano_exampleplugin"

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=PLUGIN_NAME_CLEAR,

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.0.1',

    description='SONATA example plugin 1',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/sonata-nfv/son-mano-framework/',

    # Author details
    author='SONATA',
    author_email='info@sonata-nfv.eu',

    # Choose your license
    license='Apache 2.0',

    packages=find_packages(),
    install_requires=['pika', 'pytest'],
    setup_requires=['pytest-runner'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            '%s=%s.__main__:main' % (PLUGIN_NAME, PLUGIN_NAME_CLEAR),
        ],
    },
)