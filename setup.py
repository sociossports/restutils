from setuptools import setup

setup(
    name='Django REST utils',
    version='1.2',
    packages=[
        'restutils',
        'restutils.lib',
    ],
    install_requires=[
        'isodate',
    ],
)

