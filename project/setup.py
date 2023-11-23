from distutils.core import setup
from setuptools import find_packages

setup(
    name='02242_project',
    version='0.1',
    packages=find_packages(include=['project', 'project.*'])
)