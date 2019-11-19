from setuptools import setup

setup(
    name='Django REST utils',
    version='3.0',
    packages=[
        'restutils',
        'restutils.lib',
    ],
    install_requires=[
        'isodate',
    ],
)

