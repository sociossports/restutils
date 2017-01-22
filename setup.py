from setuptools import setup

setup(
    name='Django REST utils',
    version='2.0',
    packages=[
        'restutils',
        'restutils.lib',
    ],
    install_requires=[
        'isodate',
    ],
)

