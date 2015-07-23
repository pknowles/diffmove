#!/usr/bin/python

import re
import difflib
import Levenshtein

def differences_ops(a, b):
	print "diff", repr(a), repr(b)
	sm = difflib.SequenceMatcher(None, a, b)
	ops = [((i, 0),) + t for i, t in enumerate(sm.get_opcodes())]
	builds = [op for op in ops if op[1] == 'equal']
	inserts = [op for op in ops if op[1] in ('insert', 'replace')]
	deletes = [op for op in ops if op[1] in ('delete', 'replace')]
	moves = []
	for build in builds:
		build_text = b[build[4]:build[5]]
		#print build[0], repr(build_text)
	for insert in inserts:
		#if insert[5] - insert[4] < 10:
		#	continue
		insert_text = b[insert[4]:insert[5]]
		mops = []
		for delete in deletes:
			#if delete[3] - delete[2] < 10:
			#	continue
			delete_text = a[delete[2]:delete[3]]
			#print repr(delete_text), repr(insert_text)
			d = differences_ops(delete_text, insert_text)
			
			#convert sub-operations to globals
			print "before", d
			d = [((insert[0][0], i[0]), op.replace('equal', 'move'), delete[2] + i1, delete[2] + i2, insert[4] + j1, insert[4] + j2) for i, op, i1, i2, j1, j2 in d]
			print "after", d
			mops += [(len(d), d)]
		
		print "#"*4, repr(insert_text), "mops", mops
		moves += min(mops)[1]
	print "builds", builds
	print "moves", moves
	r = [((i, 0),) + t[1:] for i, t in enumerate(sorted(builds + moves))]
	print "r", r
	return r

def differences_recursive(a, b):
	ops = differences_ops(a, b)
	
	for o in ops:
		print o[1], a[o[2]:o[3]], b[o[4]:o[5]]
	
	return ""


class DiffOp(object):
	def __init__(self, t, a, b):
		self.o, self.i1, self.i2, self.j1, self.j2 = t
		self.size = self.j2 - self.j1 if self.o == 'insert' else self.i2 - self.i1
		self.a = a
		self.b = b
		self.children = []
	
	def __len__(self):
		return self.size
	
	def __str__(self):
		if self.o == 'insert': return self.b[self.j1:self.j2]
		else: return self.a[self.i1:self.i2]
	
	def __repr__(self):
		o = {'equal':'=','delete':'-','insert':'+','move':'<','replace':'x'}[self.o]
		if o == 'move':
			t = self.a[self.i1-6:self.i1] + '[' + self.a[self.i1:self.i2] + ']' + self.a[self.i2:self.i2+6]
		else:
			t = self.__str__()
		return 'Op(' + o + t.replace('\n', ' ').strip() + ')'
	
	def __getitem__(self, i):
		if isinstance(i, slice):
			assert self.o is not 'move'
			assert i.step is None
			i = i.indices(self.size)
			if self.o == 'insert':
				return DiffOp((self.o, self.i1, self.i2, self.j1 + i[0], self.j1 + i[1]), self.a, self.b)
			else:
				return DiffOp((self.o, self.i1 + i[0], self.i1 + i[1], self.j1, self.j2), self.a, self.b)
		return self.__str__()[i]
	
	def create_move(self):
		assert self.o == 'delete'
		return DiffOp(('move', self.i1, self.i2, self.j1, self.j2), self.a, self.b)

class SmartDifferencer(object):
	def __init__(self, a, b):
		self.a = a
		self.b = b
		self.ops = self.get_codes(self.a, self.b)
		self.insertions = [op for op in self.ops if op.o == 'insert']
		
		canary = 100
		while self.bust_a_move(10):
			canary -= 1
			if canary < 0:
				break
	
	def get_codes(self, a, b):
		ops = difflib.SequenceMatcher(None, a, b).get_opcodes()
		#ops = Levenshtein.opcodes(a, b)
		r = []
		for op in ops:
			if op[0] == 'replace':
				r += [DiffOp(('delete',) + op[1:], a, b)]
				op = ('insert',) + op[1:]
			r += [DiffOp(op, a, b)]
		return r
		
	def __str__(self):
		r = ''
		for op in self.all():
			if op.o != 'delete':
				r += str(op)
		return r
		
	def __repr__(self):
		return '\n'.join(map(repr, self.all()))
	
	def all(self, t = None):
		next = list(self.ops)
		while len(next):
			op = next.pop(0)
			if op.children:
				next = op.children + next
			elif t is None or op.o == t:
				yield op
	
	def check(self):
		assert str(self) == self.b
	
	def get_biggest_insertions(self):
		return [s[1] for s in sorted([(op.size, op) for op in self.all('insert')])]
	
	def do_move(self, insert, delete, match):
		insert_before = insert[:match.a]
		move = delete[match.b:match.b + match.size].create_move()
		insert_after = insert[match.a + match.size:]
		insert.children = [insert_before, move, insert_after]
		
		delete_before = delete[:match.b]
		delete_after = delete[match.b+match.size:]
		delete.children = [delete_before, delete_after]

	def bust_a_move(self, minSize = 1):
		longest = None
		for ins in self.get_biggest_insertions():
			for d in self.all('delete'):
				sm = difflib.SequenceMatcher(None, str(ins), str(d))
				match = sm.find_longest_match(0, len(ins)-1, 0, len(d)-1)
				#print repr(ins), repr(d)
				if not match or match.size < minSize:
					continue
				if not longest or longest[0].size < match.size:
					longest = (match, d)
		
			if longest:
				self.do_move(ins, longest[1], longest[0])
				return True
		return False

if __name__ == '__main__':

	A = "Legend (in order): deleted text, , block move mark, moved block, single charater changes, highlighted and block mark, and aligned to line."
	B = "Legend (in order): , inserted text, block move mark, single chaacter changes, highlighted moved block and block mark, and ambiguous insertion aligned to line."
	
	d = SmartDifferencer(A, B)
	print repr(d)
	print d
	d.check()






