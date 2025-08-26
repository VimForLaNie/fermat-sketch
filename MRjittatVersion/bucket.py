import random
max_rc = 4
class Bucket() :
	def __init__(self,p):
		self.count = 0
		self.id = 0
		self.p = p
		self._a = random.randint(1, max_rc)
		self._b = random.randint(1, max_rc)
		pass
	
	def g(self, x) :
		# arr = [1,2,3,4]
		arr = [i for i in range(1,max_rc+1)]
		return arr[(self._a * x + self._b) % (max_rc)]
		# return x % max_rc
		# return arr[x % len(arr)]

	def insert(self, flow_id):
		print(f"g({flow_id}) = ",self.g(flow_id))
		self.count += self.g(flow_id)
		self.id += self.g(flow_id) * flow_id 

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
