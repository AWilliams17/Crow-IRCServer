from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='Crow-IRCServer',
    version='1.0.0',
    description='IRC Server implemented in Python via the Twisted framework.',
    url='https://github.com/AWilliams17/Crow-IRCServer/',
    author='Austin Williams',
    author_email='awilliams17412@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Framework :: Twisted'
        'License :: Freeware'
        'Topic :: Communications :: Chat :: Internet Relay Chat'
        'Programming Language :: Python :: 3.7',
    ],

    keywords='twisted twisted-irc irc-server',
    packages=find_packages(exclude=['tests']),

    install_requires=['twisted'],

    entry_points={
        'console_scripts': [
            'server=bin.main:main',
        ],
    },

    project_urls={
        'Bug Reports': 'https://github.com/AWilliams17/Crow-IRCServer/issues',
        'Source': 'https://github.com/AWilliams17/Crow-IRCServer/',
    },
)
