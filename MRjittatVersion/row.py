import random
from MrjittatVersion.bucket import Bucket
from kbucket import Kbucket
from MrJittacore import matrix_rank_finite_field, brute_force_k2_2d, inverse_matrix

class Rows() :
	def __init__(self,m,p):
		self.kbuckets = [Kbucket(p) for _ in range(m)]
		self._a = random.randint(1, p - 1)
		self._b = random.randint(0, p - 1)
		pass

	def hash(self, f):
		return ((self._a * f + self._b) % self.p) % self.bucket_size

	def insert(self, f):
		h = self.hash(f)
		self.kbuckets[h].insert(f)
		return h

	def pure_verification(self, i) :
		a = [bucket.id for bucket in self.kbuckets[i]]
		for g in brute_force_k2_2d(self.k) :
			try :
				inv = inverse_matrix(g)
				c = inv @ a 
				b = b @ c
				inv = inverse_matrix(b)
				f = b @ inv
				for fi in f :
					if self.hash(fi) != i :
						break
				return [(f[i],c[i]) for i in range(len(f))]
			except : 
				pass
		return []

	
	def delete(self, f, cnt) :
		h = self.hash(f)
		self.kbuckets[h].delete(f,cnt)
	