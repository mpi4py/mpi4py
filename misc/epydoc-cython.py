#!/usr/bin/env python

# --------------------------------------------------------------------

import re

# [XX] todo: add optional type modifiers?
_SIGNATURE_RE = re.compile(
    # Class name (for builtin methods)
    r'^\s*((?P<class>\w+)\.)?' +
    # The function name (must match exactly) [XX] not anymore!
    r'(?P<func>\w+)' +
    # The parameters
    ## r'\((?P<params>(\s*\[?\s*\*{0,2}[\w\-\.]+(\s*=.+?)?'+
    ## r'(\s*\[?\s*,\s*\]?\s*\*{0,2}[\w\-\.]+(\s*=.+?)?)*\]*)?)\s*\)' +
    r'\(((?P<self>(?:self|cls)),?)?(?P<params>.*)\)' +
    # The return value (optional)
    r'(\s*(->)\s*(?P<return>\S.*?))?'+
    # The end marker
    r'\s*(\n|\s+(--|<=+>)\s+|$|\.\s+|\.\n)')
"""A regular expression that is used to extract signatures from
docstrings."""

from epydoc import docstringparser as dsp
dsp._SIGNATURE_RE = _SIGNATURE_RE

# --------------------------------------------------------------------

from epydoc.cli import cli
cli()

# --------------------------------------------------------------------
