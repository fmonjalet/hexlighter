#!/usr/bin/env python

from setuptools import setup

setup(
    name='hexlighter',
    version='0.1',
    description='A hex and binary black box analysis tool',
    author='Florent Monjalet',
    author_email='florent.monjalet@gmail.com',
    package_dir = {'': 'src'},
    packages=['hexlighter'],
    scripts=['scripts/hexlighter']
)

