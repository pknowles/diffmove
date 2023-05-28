#!/usr/bin/env python

from difflib import *
from diffmove import *

a = "The quick lazy dog"
b = "The quick jumped over brown fox the lazy dog"
c = "The quick brown fox jumped over the lazy dog"
d = "The quick ... something... over the lazy dog. Oh that's right, 'brown fox jumped'."

#print SequenceMatcher(None, c, d).get_opcodes()
print('\n'.join(map(repr, SmartDifferencer(c, d, min_move_length=3, min_equal_size=3).get_diff())))
