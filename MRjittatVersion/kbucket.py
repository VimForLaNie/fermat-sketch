import random
from bucket import Bucket
from MrJittacore import matrix_rank_finite_field, brute_force_k2_2d, inverse_matrix
class Kbucket() :
	def __init__(self,k,p,rc):
		self.buckets = [Bucket(p,rc) for _ in range(k)]
		self.k = k
		pass

	def insert(self, f):
		g = []
		for bucket in self.buckets:
			g.append(bucket.insert(f))
		return g
	
	def delete(self, f, cnt) :
		for bucket in self.buckets:
			bucket.delete(f,cnt)
	