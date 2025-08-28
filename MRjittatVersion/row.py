import random
from bucket import Bucket
from kbucket import Kbucket
from MrJittacore import matrix_rank_finite_field, brute_force_k2_2d, inverse_matrix
import numpy as np

class Rows() :
	def __init__(self,m,p,k,rc):
		self.kbuckets = [Kbucket(k,p,rc) for _ in range(m)]
		self.p = p
		self.m = m
		self._a = random.randint(1, p - 1)
		self._b = random.randint(0, p - 1)
		self.k = k
		self.rc = rc
		pass

	def hash(self, f):
		return ((self._a * f + self._b) % self.p) % self.m

	def insert(self, f):
		h = self.hash(f)
		print(f,h)
		return self.kbuckets[h].insert(f)
		# return h

	def pure_verification(self, i) :
		a = np.array([bucket.count for bucket in self.kbuckets[i].buckets], dtype=int).reshape(-1, 1)
		id = np.array([bucket.id for bucket in self.kbuckets[i].buckets], dtype=int).reshape(-1, 1)
		answer = []
		# print(a)
		count = 0
		for g in brute_force_k2_2d(self.k,self.rc) :
			g = np.array(g, dtype=int)
			rank =  np.linalg.matrix_rank(g)
			# print("rank",rank)
			if rank < 3 :
				continue
			try :
				inv = inverse_matrix(g)
				c = (inv @ a)
				if not np.allclose(c, np.round(c), atol=1e-10):
					continue
				if np.any(c < 0) :
					continue
				c = np.round(c).astype(int)
				c_diag = np.diagflat(c)
				gc = (g @ c_diag) 
				gc_inv = inverse_matrix(gc)
				f = (gc_inv @ id)
				#close round
				if not np.allclose(f, np.round(f), atol=1e-10):
					continue
				f = np.round(f).astype(int)
				flag = True
				for idx in range(len(f)) :
					if self.hash(int(f[idx][0])) != i :
						flag = False
						break
				for j in range(len(g)) :
					for k in range(len(f)):
						# print(f"g[{j}][{k}] = {g[j][k]}, bucket.g({int(f[k][0])}) = {self.kbuckets[i].buckets[j].g(int(f[k][0]))}")
						if self.kbuckets[i].buckets[j].g(int(f[k][0])) != g[j][k] :
							flag = False
							break
				if flag :
					print(f"found pure: {f.flatten()}, count: {c.flatten()}")
					answer.append( [(int(f[idx][0]), int(c[idx][0])) for idx in range(len(f))])
			except np.linalg.LinAlgError : 
				# print("not invertible")
				pass
		return answer
	

	
	def delete(self, f, cnt) :
		# print(f)
		h = self.hash(f)
		# print(h)
		self.kbuckets[h].delete(f,cnt)
	