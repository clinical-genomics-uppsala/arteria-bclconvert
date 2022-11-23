from setuptools import setup, find_packages
from bclconvert import __version__
import os

def read_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

try:
    with open("requirements.txt", "r") as f:
        install_requires = [x.strip() for x in f.readlines()]
except IOError:
    install_requires = []

setup(
    name='bclconvert',
    version=__version__,
    description="Micro-service for running bcl-convert",
    long_description=read_file('README.md'),
    keywords='bioinformatics',
    author='Clinical Genomics, Uppsala University',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': ['bclconvert-ws = bclconvert.app:start']
    },
    #install_requires=install_requires
)
