from setuptools import setup, find_packages

setup(
    name='lumen',
    classfiers=[
        'Private :: Do Not Upload',
    ],
    packages=find_packages(exclude='tests'),
    install_requires=[
        'Flask',
        'gunicorn',
    ],
)
