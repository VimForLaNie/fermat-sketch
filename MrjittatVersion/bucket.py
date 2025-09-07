import random

prime = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97, 101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,179,181,191,193,197,199]
class Bucket() :
	def __init__(self,p,rc,k):
		self.count = 0
		self.id = 0
		self.p = p
		self.rc = rc
		self._a = random.randint(1, p - 1)
		self._b = random.randint(0, p - 1)
		self.k = k
		# print("Bucket init _a",self._a,"_b",self._b)
		pass
	
	def g(self, f, i) :
		arr = [[prime[i + j * self.rc] for i in range(self.rc)] for j in range(self.k)]
		# print("g array",arr)
		# arr = [419,569,241,151,29,13]
		return arr[i][(self._a * f + self._b) % self.p % (self.rc)]


	def insert(self, flow_id, i):
		# print(f"g({flow_id}) = ",self.g(flow_id,i))
		self.count += self.g(flow_id,i)
		self.id += self.g(flow_id,i) * flow_id 
		return self.g(flow_id,i)

	def delete(self, flow_id, cnt,i):
		if self.count < cnt * self.g(flow_id,i) :
			self.count = 0
		self.count -= cnt * self.g(flow_id,i)
		self.id = (self.id - self.g(flow_id,i) * flow_id * cnt) % self.p 
	
				

	# def is_pure(self, j , hash, f = None) :
	# 	if self.count <= 0 :
	# 		return False
	# 	f_prime = self.id * power(self.count,self.p -2,self.p)
	# 	if hash(f_prime) != j :
	# 		return False
	# 	return True

	def get_sumid_and_count(self) :
		sum_id = self.id * power(self.count, self.p - 2, self.p)
		return sum_id, self.count

def power(a,b,p) :
	return pow(a, b, p)
