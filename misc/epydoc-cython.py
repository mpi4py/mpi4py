#! /usr/bin/env python

# --------------------------------------------------------------------

import re

_SIGNATURE_RE = re.compile(
    # Class name (for builtin methods)
    r'^\s*((?P<class>\w+)\.)?' +
    # The function name
    r'(?P<func>\w+)' +
    # The parameters
    r'\(((?P<self>(?:self|cls|mcs)),?)?(?P<params>.*)\)' +
    # The return value (optional)
    r'(\s*(->)\s*(?P<return>\S.*?))?'+
    # The end marker
    r'\s*(\n|\s+(--|<=+>)\s+|$|\.\s+|\.\n)')

from epydoc import docstringparser as dsp
dsp._SIGNATURE_RE = _SIGNATURE_RE

# --------------------------------------------------------------------

from epydoc.cli import cli
cli()

# --------------------------------------------------------------------
