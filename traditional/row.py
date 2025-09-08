import random
from bucket import Bucket
class Rows() :
	def __init__(self,size,p):
		self.size = size
		self.buckets = [Bucket(p) for _ in range(size)]
		self._a = random.randint(1, p - 1)
		self._b = random.randint(0, p - 1)
		self.p = p
		self.bucket_size = size

	def hash_index(self, f):
		return ((self._a * f + self._b) % self.p) % self.bucket_size

	def insert(self, f):
		h = self.hash_index(f)
		self.buckets[h].insert(f)
		return h

	
	def delete(self, f, cnt) :
		h = self.hash_index(f)
		self.buckets[h].delete(f,cnt)
			
				

