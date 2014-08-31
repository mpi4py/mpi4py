#!/usr/bin/env python
# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Wrapper to run setup.py using setuptools."""
import setuptools
f = open('setup.py', 'rb')
try:
    exec(compile(f.read(), 'setup.py', 'exec'))
finally:
    f.close()
