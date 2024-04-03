from setuptools import setup, find_packages

setup(
    name='book-data-pipeline',
    version='0.1.0',
    description='src package for spark processing jobs in book data pipeline project',
    packages=find_packages(include=['src', 'src.*']),
)