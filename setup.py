#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-enumfield',
    description="Type-safe, efficient & database-agnostic enumeration field "
        'for Django.',
    version="0.1",

    author='Chris Lamb',
    author_email='chris@chris-lamb.co.uk',
    license='BSD',

    packages=find_packages(),
)
