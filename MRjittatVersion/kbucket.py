import random
from MrjittatVersion.bucket import Bucket
from MrJittacore import matrix_rank_finite_field, brute_force_k2_2d, inverse_matrix
class Kbucket() :
	def __init__(self,k,p):
		self.kbucket = [Bucket(p) for _ in range(k)]
		self.k = k
		pass

	def insert(self, f):
		for bucket in self.kbucket:
			bucket.insert(f)
	
	def delete(self, f, cnt) :
		for bucket in self.kbucket:
			bucket.delete(f,cnt)
	
	def pure_verification(self, i,hash) :
		a = [bucket.id for bucket in self.kbucket]
		for g in brute_force_k2_2d(self.k) :
			try :
				inv = inverse_matrix(g)
				c = inv @ a 
				b = b @ c
				inv = inverse_matrix(b)
				f = b @ inv
				
			except : 
				pass
