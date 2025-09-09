from collections import deque, defaultdict
import numpy as np

import random
# from kbucket import Kbucket
# from MrJittacore import brute_force_k2_2d, inverse_matrix
import numpy as np

import random
import random


def generate_primes(n):
	primes = []
	candidate = 2
	while len(primes) < n:
		for p in primes:
			if candidate % p == 0:
				break
		else:
			primes.append(candidate)
		candidate += 1
	return primes

class Bucket() :
	def __init__(self,p,rc,k,primes=None):
		self.count = 0
		self.id = 0
		self.p = p
		self.rc = rc
		self._a = random.randint(1, p - 1)
		self._b = random.randint(0, p - 1)
		self.k = k
		self.primes = primes if primes is not None else generate_primes(k * rc)
	
	def g(self, f, i) :
		arr = [[self.primes[i + j * self.rc] for i in range(self.rc)] for j in range(self.k)]
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

class Kbucket() :
	def __init__(self,k,p,rc,primes=None):
		if primes is None:
			primes = generate_primes(k * rc)
		self.buckets = [Bucket(p,rc,k,primes) for _ in range(k)]
		self.k = k

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
	

from itertools import product
import numpy as np

def brute_force_k2_2d(k, rc, primes=None):
	"""
	Generate k x k matrices where each entry is chosen from 0..rc-1,
	then mapped through primes[index + i*rc].
	"""
	length = k * k
	needed = k * rc
	if primes is None:
		primes = generate_primes(needed)
	for combo in product(range(0, rc), repeat=length):
		mat_indices = [list(combo[i*k:(i+1)*k]) for i in range(k)]
		matrix = [[primes[mat_indices[i][j] + i * rc] for j in range(k)] for i in range(k)]
		yield matrix


# ---------- modular inverse for matrices via Gauss-Jordan mod p ----------
def matrix_mod_inverse(A, p):
	"""
	Compute inverse of integer matrix A modulo prime p.
	A: list of lists or 2D numpy array (square)
	returns: numpy.ndarray (dtype=int) of shape (n,n) with values in 0..p-1
	raises: ValueError if singular modulo p
	"""
	A = np.array(A, dtype=int) % p
	n = A.shape[0]
	if A.shape[0] != A.shape[1]:
		raise ValueError("Only square matrices can be inverted")

	# build augmented matrix [A | I]
	aug = np.hstack([A.copy(), np.eye(n, dtype=int)])
	# perform Gauss-Jordan elimination modulo p
	for col in range(n):
		# find pivot row with non-zero in this column
		pivot = None
		for r in range(col, n):
			if aug[r, col] % p != 0:
				pivot = r
				break
		if pivot is None:
			raise ValueError("Matrix is singular modulo p")

		# swap pivot row into place
		if pivot != col:
			aug[[col, pivot]] = aug[[pivot, col]]

		# normalize pivot row: multiply by inv(pivot_val) mod p
		pivot_val = int(aug[col, col] % p)
		inv_pivot = pow(pivot_val, p - 2, p)  # p should be prime; uses Fermat
		aug[col, :] = (aug[col, :] * inv_pivot) % p

		# eliminate other rows
		for r in range(n):
			if r == col:
				continue
			factor = int(aug[r, col] % p)
			if factor != 0:
				aug[r, :] = (aug[r, :] - factor * aug[col, :]) % p

	inv = aug[:, n:] % p
	return inv.astype(int)


def inverse_matrix(matrix, p=None):
	"""
	If p is provided -> return modular inverse over GF(p) as numpy int array.
	If p is None -> return standard numpy.linalg.inv (float).
	"""
	mat = np.array(matrix)
	if p is None:
		return np.linalg.inv(mat.astype(float))
	else:
		return matrix_mod_inverse(mat, p)


class Rows:
	def __init__(self, m, p, k, rc, use_modular=False):
		self.kbuckets = [Kbucket(k, p, rc) for _ in range(m)]
		self.p = p
		self.m = m
		self._a = random.randint(1, p - 1)
		self._b = random.randint(0, p - 1)
		self.k = k
		self.rc = rc
		self.use_modular = use_modular  # if True, attempt modular inverses via inverse_matrix(..., p)
		# Cache all brute force matrices for this row
		self.brute_force_matrices = {}
		for kk in range(self.k, 0, -1):
			self.brute_force_matrices[kk] = list(brute_force_k2_2d(kk, self.rc))

	def hash(self, f):
		return ((self._a * f + self._b) % self.p) % self.m

	def insert(self, f):
		h = self.hash(f)
		return self.kbuckets[h].insert(f)

	def pure_verification(self, i):
		"""
		Attempt to decode bucket i. Returns list of (flow_id, count) pairs
		for first valid solution found (same behavior as original).
		"""
		# get the buckets for this kbucket (list of Bucket instances)
		buckets = self.kbuckets[i].buckets

		# try decreasing kk from self.k down to 1
		for kk in range(self.k, 0, -1):
			# build column vectors a and id from the first kk buckets
			a = np.array([buckets[idx].count for idx in range(kk)], dtype=int).reshape(-1, 1)
			id_vec = np.array([buckets[idx].id for idx in range(kk)], dtype=int).reshape(-1, 1)

			# if all counts are zero, nothing to do
			if np.count_nonzero(a) == 0:
				continue

			# iterate candidate g matrices from cache
			for g_candidate in self.brute_force_matrices[kk]:
				g = np.array(g_candidate, dtype=float)  # use float for numeric inversion
				# quick rank check (floating). If rank < kk skip
				try:
					rank = np.linalg.matrix_rank(g)
				except Exception:
					# numerical issue computing rank => skip candidate
					continue
				if rank < kk:
					continue

				# Try to invert g (either modular or float)
				try:
					if self.use_modular:
						# inverse_matrix expected to support modular inverse when given p
						inv_g = inverse_matrix(g_candidate, self.p)  # ensure MrJittacore supports this signature
						inv_g = np.array(inv_g, dtype=float)  # convert to float for further arithmetic
					else:
						# float inverse
						# skip ill-conditioned matrices to reduce numeric instability:
						cond = np.linalg.cond(g)
						if not np.isfinite(cond) or cond > 1e12:
							# ill-conditioned, skip
							continue
						inv_g = np.linalg.inv(g)
					# compute c = inv_g @ a
					c_d = inv_g @ a.astype(float)

					# require c to be integer-ish and non-negative
					if not np.allclose(c_d, np.round(c_d), atol=1e-8):
						continue
					c = np.round(c_d).astype(int).reshape(-1, 1)
					if np.any(c < 0):
						continue

					# form diag(c) and attempt to invert gc = g * diag(c)
					c_diag = np.diagflat(c.flatten())
					gc = g @ c_diag

					# check invertibility of gc
					# skip if gc is ill-conditioned or rank < kk
					if np.linalg.matrix_rank(gc) < kk:
						continue
					cond_gc = np.linalg.cond(gc)
					if not np.isfinite(cond_gc) or cond_gc > 1e12:
						continue

					if self.use_modular:
						gc_inv = inverse_matrix(gc.astype(int).tolist(), self.p)
						gc_inv = np.array(gc_inv, dtype=float)
					else:
						gc_inv = np.linalg.inv(gc)

					f_d = gc_inv @ id_vec.astype(float)
					if not np.allclose(f_d, np.round(f_d), atol=1e-8):
						continue
					f = np.round(f_d).astype(int).reshape(-1, 1)

					# verify that each recovered flow hashes to this bucket i
					ok = True
					for idx in range(len(f)):
						if self.hash(int(f[idx, 0])) != i:
							ok = False
							break
					if not ok:
						continue

					# verify g-consistency: bucket.g(flow, row) == g[row, col]
					for row in range(kk):
						for col in range(kk):
							flow_candidate = int(f[col, 0])
							expected_g = int(round(g[row, col]))
							# call bucket.g with (flow_candidate, row)
							if buckets[row].g(flow_candidate, row) != expected_g:
								ok = False
								break
						if not ok:
							break
					if not ok:
						continue

					# success -> return solution (flow, count) pairs
					result = [(int(f[j, 0]), int(c[j, 0])) for j in range(kk)]
					return result

				except Exception:
					# catch any numeric or modular-inversion failures and skip this candidate
					continue

		# nothing found
		return []

	def delete(self, f, cnt):
		h = self.hash(f)
		self.kbuckets[h].delete(f, cnt)

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
				if kbucket.buckets[0].count > 0:
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

