#!/usr/bin/env python

from difflib import *
from diffmove import *

s0 = "The quick lazy dog"
s1 = "The quick jumped over brown fox the lazy dog"
s2 = "The quick brown fox jumped over the lazy dog"
s3 = "The quick ... something... over the lazy dog. Oh that's right, 'brown fox jumped'."

a0 = "aaaaaaaaaa"
a1 = "baaabbbaaaaaaa"
a2 = "baaaaaaabbaaa"
a3 = "bbbaaa bbbaaa bbbaaa bbbaaa bbbaaam bbbaaa"
a4 = "ac bbbaaam bbbaaac bbbaaac bbbaaac bbbaaac bbbaa"

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
        ('equal', 'The quick'),
        ('insert', ' '), # TODO: why does this space need a separate insert?
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
    (a0, a1, [
        ('insert', 'b'),
        ('move', 'aaa'), # TODO: it would be nicer if moves were not created
        ('insert', 'bbb'),
        ('equal', 'aaaaaaa'),
        ('delete', 'aaa'),
    ]),
    (a1, a2, [
        # Works, but not the way I would have done it
        ('delete', 'baaabb'),
        ('equal', 'baaaaaaa'),
        ('insert', 'b'),
        ('move', 'baaa'),
    ]),
    (a3, a4, [
        # Works, but not the way I would have done it
        ('delete', 'bbbaaa bbbaaa bbbaaa bbbaaa'),
        ('insert', 'ac'),
        ('equal', ' bbbaaam bbbaaa'),
        ('insert', 'c'),
        ('move', ' bbbaaa'),
        ('insert', 'c'),
        ('move', ' bbbaaa'),
        ('insert', 'c'),
        ('move', ' bbbaaa'),
        ('insert', 'c '),
        ('move', 'bbbaa'),
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
            print("        " + repr(op) + ",")
print("Done")
