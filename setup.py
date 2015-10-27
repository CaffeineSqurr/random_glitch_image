import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='vitium',
    version='0.1',
    author = 'Elliot Branson',
    py_modules=['vitium'],
    packages=['vitium'],
    install_requires=[
	'requests',
        'jpglitch',
        'Pillow',
    ],
    dependency_links=[
        'git+ssh://git@github.com:Kareeeeem/jpglitch.git'
    ],
    long_description=read('README'),
    entry_points='''
        [console_scripts]
        vitium=vitium:cli
    ''',
)
