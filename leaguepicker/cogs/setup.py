from setuptools import setup

setup(
    name='leaguepicker',
    version='1.0.0',
    packages=['leaguepicker'],
    install_requires=[
        'discord.py'
        './cogs'
    ]
)
