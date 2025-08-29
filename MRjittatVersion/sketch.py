from collections import deque, defaultdict
import numpy as np
import random

prime = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
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
		arr = [[prime[i + j * self.rc] for i in range(self.rc)] for j in range(self.rc)]
		# print("g array",arr)
		# arr = [419,569,241,151,29,13]
		return arr[i][(self._a * f + self._b) % self.p % (self.rc)]


	def insert(self, flow_id, i):
		# print(f"g({flow_id}) = ",self.g(flow_id,i))
		self.count += self.g(flow_id,i)
		self.id += self.g(flow_id,i) * flow_id 
		return self.g(flow_id,i)

	def delete(self, flow_id, cnt,i):
		self.count -= cnt
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

import random
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

import random
import numpy as np

from itertools import product

def brute_force_k2_2d(k,rc):
    length = k * k
    prime = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
    for combo in product(range(0, rc), repeat=length):  # 1..k instead of 0..k-1
    # for combo in product([2,3,5,7,11,13,17,19][:rc], repeat=length):  # 1..k instead of 0..k-1
        matrix = [list(combo[i*k:(i+1)*k]) for i in range(k)]
        matrix = [[prime[matrix[i][j] + i * rc] for j in range(k)] for i in range(k)]
        # print(f"Trying matrix: {matrix}")
        yield matrix
        
import numpy as np

def inverse_matrix(matrix, p = None):
    """
    Compute the inverse of a matrix using NumPy.
    
    Args:
        matrix (list[list[float]] or np.ndarray): The square matrix.
        
    Returns:
        np.ndarray: The inverse matrix.
    """
    if p is not None :
        matrix = np.array(matrix, dtype=int) % p
        inv = np.linalg.inv(matrix).astype(int) % p
        for i in range(len(inv)) :
            for j in range(len(inv)) :
                inv[i][j] = inv[i][j] % p
        return inv
    else :
        return np.linalg.inv(matrix)

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
		# print(f,h)
		return self.kbuckets[h].insert(f)
		# return h

	def pure_verification(self, i) :

		answer = []
		# print(a)
		count = 0
		for kk in range(1,self.k + 1) :
			a = np.array([bucket.count for bucket in self.kbuckets[i].buckets][:kk], dtype=int).reshape(-1, 1)
			id = np.array([bucket.id for bucket in self.kbuckets[i].buckets][:kk], dtype=int).reshape(-1, 1)
			for g in brute_force_k2_2d(kk,self.rc) :
				g = np.array(g, dtype=int)
				# print("g",g)
				# rank =  np.linalg.matrix_rank(g)
				# print("rank",rank)
				# if rank < 3 :
				# 	continue
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
							if self.kbuckets[i].buckets[j].g(int(f[k][0]),j) != g[j][k] :
								flag = False
								break
					if flag :
						# print(f"found pure: {f.flatten()}, count: {c.flatten()}")
						return [(int(f[j][0]),int(c[j][0])) for j in range(len(f))]
						answer.append( [(int(f[idx][0]), int(c[idx][0])) for idx in range(len(f))])
				except np.linalg.LinAlgError : 
					# print("not invertible")
					pass
		return []

	
	def delete(self, f, cnt) :
		# print(f)
		h = self.hash(f)
		# print(h)
		self.kbuckets[h].delete(f,cnt)

class Sketch :
	def __init__(self, rows_cnt, buckets_cnt, p,k,rc) :
		self.rows_cnt = rows_cnt
		self.p = p
		self.rows = [Rows(buckets_cnt, p,k,rc) for _ in range(rows_cnt)]
		self.pure_elements = []
		self.flowset = defaultdict(int)
		self.k = k

	def verify(self):
		queue = deque()
		checked_pure = set()
		stop = 0
		for i, row in enumerate(self.rows):
			for j, kbucket in enumerate(row.kbuckets):
				if kbucket.buckets[0].count != 0:
					queue.append((i, j))
		
		while len(queue) > 0:
			# print("Queue length:", len(queue))
			# print("Current queue:", list(queue))
			i, j = queue.popleft()
			# print(f"Verifying row {i}, bucket {j}")
			# kbucket = self.rows[i].kbuckets[j]
			# print(f"Processing bucket at row {i}, index {j} with count {bucket.count} and id {bucket.id}")
			c = self.rows[i].kbuckets[j].get_count()
			if np.count_nonzero(c) == 0 :
				continue
			k = self.rows[i].pure_verification(j)
			# print("get",k)
			# break
			if len(k) == 0:
				queue.append((i, j))
				stop += 1
				if stop >= len(queue) + 1 :
					# print("Cannot decode further, stopping.")
					break
			else :
				# print("pure",k)
				for f, cnt in k:
					for row in self.rows:
						# print("delete",int(f),int(cnt))
						row.delete(f, cnt)
				self.flowset[f] += cnt
				stop = 0
		return dict(self.flowset)

	def insert(self, f):
		for row in self.rows:
			row.insert(f)

