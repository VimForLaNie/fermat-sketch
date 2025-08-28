import random
class Bucket() :
	def __init__(self,p,rc):
		self.count = 0
		self.id = 0
		self.p = p
		self.rc = rc
		self._a = random.randint(1, p - 1)
		self._b = random.randint(0, p - 1)
		pass
	
	def g(self, x) :
		# arr = [1,2,3,4]
		arr = [i for i in range(1,self.rc+1)]
		# arr = [419,569,241,151,29,13]
		return arr[(self._a * x + self._b) % (self.rc)]
		# return x % rc
		# return arr[x % len(arr)]

	def insert(self, flow_id):
		print(f"g({flow_id}) = ",self.g(flow_id))
		self.count += self.g(flow_id)
		self.id += self.g(flow_id) * flow_id 
		return self.g(flow_id)

	def delete(self, flow_id, cnt):
		self.count -= cnt
		self.id = (self.id - self.g(flow_id) * flow_id * cnt) % self.p 
				

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
