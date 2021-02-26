from setuptools import setup

setup(
    name='restutils',
    version='1.2',
    packages=[
        'restutils',
        'restutils.lib',
    ],
    install_requires=[
        'isodate',
    ],
)

