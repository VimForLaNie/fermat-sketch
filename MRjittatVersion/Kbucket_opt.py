from bucket import Bucket
class KBucket() :
	def __init__(self,p,k):
		self.buckets = [Bucket(p) for _ in range(k)]
		pass


	def insert(self, flow_id):
		self.count += 1
		self.id = (self.id + flow_id) % self.p

	def delete(self, flow_id, cnt):
		self.count -= cnt
		self.id = (self.id - flow_id) % self.p
				

	def is_pure(self, j , hash, f = None) :
		if self.count <= 0 :
			return False
		f_prime = self.id * power(self.count,self.p -2,self.p)
		if hash(f_prime) != j :
			return False
		return True

	def get_sumid_and_count(self) :
		sum_id = self.id * power(self.count, self.p - 2, self.p)
		return sum_id, self.count


def power(a,b,p) :
	return pow(a, b, p)
