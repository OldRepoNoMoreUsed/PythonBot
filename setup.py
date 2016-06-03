"""Setup d'Alonso permet son installation et l'installation de ces dépendances via pip"""

from setuptools import setup, find_packages

setup(
    name='BotAlonso',
    version='1.0',
    description=__doc__,
    packages=find_packages(),
    install_requires=(
        "aiohttp",
        "websocket",
        "slackclient",
        "pyinotify",
    ),
    extras_require={
        "test": ("pytest",),
        "doc": ('Sphinx', 'sphinx_rtd_theme'),
    }
)