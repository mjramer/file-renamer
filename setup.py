from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name='file-renamer',
    version='0.1',
    author='Max Ramer', 
    author_email='maxjramer@gmail.com',
    packages=find_packages(),
    long_description=open('README.md').read()
)