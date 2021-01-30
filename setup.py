from setuptools import setup

setup(
    name='restutils',
    version='3.0',
    packages=[
        'restutils',
        'restutils.lib',
    ],
    install_requires=[
        'isodate',
    ],
)

