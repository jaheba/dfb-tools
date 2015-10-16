

from setuptools import setup


setup(
    name='Soca',
    version='0.1',
    packages=['soca'],
    install_requires=[
        'click',
        'lxml',
    ],
    entry_points={
        'console_scripts': 'soca=soca.soca:cli'
    },
)
