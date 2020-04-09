import os
from setuptools import setup, find_packages

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
long_description = open(BASE_DIR + '/README.md').read()

setup(
    name='diplomacy_adjudicator',
    url='https://github.com/johnpooch/diplomacy-adjudicator',
    version='0.0.1',
    author="John McDowell",
    description='An adjudicator for the board game Diplomacy.',
    long_description=long_description,
    install_requires=[],
    include_package_data=True,
    packages=find_packages(exclude=('tests',)),
    python_requires='>=3.6',
)

