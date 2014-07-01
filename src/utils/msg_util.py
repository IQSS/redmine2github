from __future__ import print_function

import sys
# Just the print statement...

def msg(s): print(s)
def dashes(): msg(40*'-')
def msgt(s): dashes(); msg(s); dashes()
def msgx(s): msgt(s); sys.exit(0)
