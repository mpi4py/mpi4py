#!/usr/bin/env python
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import cyautodoc
from Cython.Compiler.Main import main
while '--no-docstrings' in sys.argv:
    sys.argv.remove('--no-docstrings')
main(command_line=1)
