import random
from .bucket import Bucket
from .MrJittacore import matrix_rank_finite_field, brute_force_k2_2d, inverse_matrix
class Kbucket() :
	def __init__(self,k,p,rc):
		self.buckets = [Bucket(p,rc,k) for _ in range(k)]
		self.k = k
		pass

	def insert(self, f):
		g = []
		for i,bucket in enumerate(self.buckets):
			g.append(bucket.insert(f,i))
		return g
	
	def delete(self, f, cnt) :
		for i,bucket in enumerate(self.buckets):
			bucket.delete(f,cnt,i)

	def get_count(self) :
		return [bucket.count for bucket in self.buckets]
	