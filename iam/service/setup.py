from os import environ
from setuptools import setup, find_packages

DEFAULT_BUILD_VERSION = "0.0.dev0"


def requirements():
    with open('requirements.txt') as r:
        return r.read().strip().split('\n')


setup(name='demo_app_iam_service',
      install_requires=requirements(),
      package_dir={'': 'src'},
      packages=find_packages('src'),
      version=environ.get('BUILD_VERSION', DEFAULT_BUILD_VERSION))
