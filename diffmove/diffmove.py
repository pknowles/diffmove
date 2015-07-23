#! /usr/bin/env python2

import difflib

class DiffOp(object):
	def __init__(self, t, a, b):
		self.o, self.i1, self.i2, self.j1, self.j2 = t
		self.size = self.j2 - self.j1 if self.o in ('insert', 'move') else self.i2 - self.i1
		self.a = a
		self.b = b
		self.children = []
		self.can_move = True
	
	def __len__(self):
		return self.size
	
	def __str__(self):
		if self.o == 'insert': return self.b[self.j1:self.j2]
		if self.o == 'move': return self.a[self.j1:self.j2]
		else: return self.a[self.i1:self.i2]
	
	def __repr__(self):
		o = {'equal':'=','delete':'-','insert':'+','move':'<','replace':'x'}[self.o]
		if o == 'move':
			t = self.a[self.i1-6:self.i1] + '[' + self.a[self.i1:self.i2] + ']' + self.a[self.i2:self.i2+6]
		else:
			t = self.__str__()
		return 'Op(' + o + (t.replace('\n', ' ').strip() or '\w') + ')'
	
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
	
	def create_move(self, insert):
		assert self.o == 'delete'
		return DiffOp(('move', insert.i1, insert.i2, self.i1, self.i2), self.a, self.b)

class SmartDifferencer(object):
	"""Behaves similarly to SequenceMatcher.get_opcodes but introduces
	a 'move' op where (j1, j2) refer to an item in A to be inserted	at i1
	
	Usage:
		diff = SmartDifferencer(a, b)
		opcodes = diff.get_opcodes()
	
	"""

	def __init__(self, a, b):
		self.a = a
		self.b = b
		self.ops = self._create_diffops(self.a, self.b)
		
		canary = 100
		while self.bust_a_move(10):
			canary -= 1
			if canary < 0:
				break
	
	def _create_diffops(self, a, b):
		ops = difflib.SequenceMatcher(None, a, b).get_opcodes()
		r = []
		for op in ops:
			# a replace is considered a delet and an insert
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
	
	def get_opcodes(self, include_replace=True):
		# the simple version
		if not include_replace:
			return [(op.o, op.i1, op.i2, op.j1, op.j2) for op in self.all()]
		
		ops = []
		last = None
		for op in self.all():
			if last:
				# all this complexity, just to provide 'replace'
				if last.o == 'delete' and op.o == 'insert':
					ops += [('replace', last.i1, last.i2, op.j1, op.j2)]
					last = None
					continue
				else:
					ops += [(last.o, last.i1, last.i2, last.j1, last.j2)]
			last = op
		if last:
			ops += [(last.o, last.i1, last.i2, last.j1, last.j2)]
		return ops
	
	def get_diff(self):
		return [(op.o, str(op)) for op in self.all()]
	
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
	
	def _get_biggest_insertions(self):
		return [s[1] for s in sorted([(op.size, op) for op in self.all('insert')])]
	
	def _do_move(self, insert, delete, match):
		insert_before = insert[:match.a]
		move = delete[match.b:match.b + match.size].create_move(insert)
		insert_after = insert[match.a + match.size:]
		insert.children = filter(lambda x: len(x) > 0, [insert_before, move, insert_after])
		
		delete_before = delete[:match.b]
		delete_middle = delete[match.b:match.b+match.size]
		delete_middle.can_move = False
		delete_after = delete[match.b+match.size:]
		delete.children = filter(lambda x: len(x) > 0, [delete_before, delete_middle, delete_after])
		
		#print "MOVE"
		#print repr(insert), repr(delete), match
		#print insert.children
		#print delete.children

	def bust_a_move(self, minSize = 1):
		longest = None
		for ins in self._get_biggest_insertions():
			for d in self.all('delete'):
				if not d.can_move:
					continue
				sm = difflib.SequenceMatcher(None, str(ins), str(d))
				match = sm.find_longest_match(0, len(ins)-1, 0, len(d)-1)
				#print repr(ins), repr(d)
				if not match or match.size < minSize:
					continue
				if not longest or longest[0].size < match.size:
					longest = (match, d)
		
			if longest:
				self._do_move(ins, longest[1], longest[0])
				return True
		return False

if __name__ == '__main__':

	A = "Legend (in order): deleted text, , block move mark, moved block, single charater changes, highlighted and block mark, and aligned to line."
	B = "Legend (in order): , inserted text, block move mark, single chaacter changes, highlighted moved block and block mark, and ambiguous insertion aligned to line."
	
	d = SmartDifferencer(A, B)
	print repr(d)
	print d.get_diff()
	print d
	d.check()
	with_move = d.get_opcodes()
	regular = difflib.SequenceMatcher(None, A, B).get_opcodes()
	
	from itertools import izip_longest
	for x, y in izip_longest(with_move, regular):
		print x, y





