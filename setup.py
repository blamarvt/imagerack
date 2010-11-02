#!/usr/bin/env python
from distutils.cmd import Command
from setuptools import setup, find_packages

__author__ = 'Brian Lamar'

setup(	
	name = 'imagerack',
	version = '0.1',
	author = __author__,
	packages = find_packages(),
	install_requires = ['gevent', 'python-daemonhelper', 'PIL'],
	entry_points = '''
	[console_scripts]
	imagerack-wsgi = imagerack.wsgi.server:main
	'''
)

