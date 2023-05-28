#!/usr/bin/env python

from difflib import *
from diffmove import *

s0 = "The quick lazy dog"
s1 = "The quick jumped over brown fox the lazy dog"
s2 = "The quick brown fox jumped over the lazy dog"
s3 = "The quick ... something... over the lazy dog. Oh that's right, 'brown fox jumped'."

tests = [
    (s0, s1, [
        ('equal', 'The quick '),
        ('insert', 'jumped over brown fox the '),
        ('equal', 'lazy dog'),
    ]),
    (s0, s2, [
        ('equal', 'The quick '),
        ('insert', 'brown fox jumped over the '),
        ('equal', 'lazy dog'),
    ]),
    (s0, s3, [
        ('equal', 'The quick '),
        ('insert', '... something... over the '),
        ('equal', 'lazy dog'),
        ('insert', ". Oh that's right, 'brown fox jumped'."),
    ]),
    (s1, s2, [
        ('equal', 'The quick '), # TODO: why does this space need a separate insert?
        ('move', 'brown fox'),
        ('equal', ' jumped over '),
        ('delete', 'brown fox '),
        ('equal', 'the lazy dog'),
    ]),
    (s2, s3, [
        ('equal', 'The quick '),
        ('delete', 'brown fox jumped'),
        ('insert', '... something...'),
        ('equal', ' over the lazy dog'),
        ('insert', ". Oh that's right, '"),
        ('move', 'brown fox jumped'),
        ('insert', "'."),
    ]),
    (s3, s2, [
        ('equal', 'The quick '),
        ('delete', '... something...'),
        ('move', 'brown fox jumped'),
        ('equal', ' over the lazy dog'),
        ('delete', ". Oh that's right, 'brown fox jumped'."),
    ]),
]

for i, (a, b, expect) in enumerate(tests):
    print("Test", i)
    #print SequenceMatcher(None, a, b).get_opcodes()
    diff = list(SmartDifferencer(a, b, min_move_length=3, min_equal_size=3).get_diff())
    if expect != diff:
        print("  Failed:")
        print("    a:", a)
        print("    b:", b)
        for op in diff:
            print("      " + repr(op))
print("Done")
