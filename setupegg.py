#!/usr/bin/env python
# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"Wrapper to run setup.py using setuptools"
import setuptools
with open('setup.py', 'rb') as f:
    exec(compile(f.read(), 'setup.py', 'exec'))
