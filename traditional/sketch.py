from collections import deque, defaultdict
import random

class Rows() :
	def __init__(self,size,p):
		self.size = size
		self.buckets = [Bucket(p) for _ in range(size)]
		self._a = random.randint(1, p - 1)
		self._b = random.randint(0, p - 1)
		self.p = p
		self.bucket_size = size

	def hash(self, f):
		return ((self._a * f + self._b) % self.p) % self.bucket_size

	def insert(self, f):
		h = self.hash(f)
		self.buckets[h].insert(f)
		return h

	
	def delete(self, f, cnt) :
		h = self.hash(f)
		self.buckets[h].delete(f,cnt)

class Bucket() :
	def __init__(self,p):
		self.count = 0
		self.id = 0
		self.p = p
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


class Sketch :
	def __init__(self, rows_cnt, buckets_cnt, p) :
		self.rows_cnt = rows_cnt
		self.p = p
		self.rows = [Rows(buckets_cnt, p) for _ in range(rows_cnt)]
		self.pure_elements = []
		self.flowset = defaultdict(int)

	def insert(self,f) :
		for row in self.rows:
			row.insert(f)

	def verify(self):
		queue = deque()
		checked_pure = set()
		for i, row in enumerate(self.rows):
			for j, bucket in enumerate(row.buckets):
				if bucket.count != 0:
					queue.append((i, j))
		while queue:
			i, j = queue.popleft()
			bucket = self.rows[i].buckets[j]
			# print(f"Processing bucket at row {i}, index {j} with count {bucket.count} and id {bucket.id}")
			if bucket.is_pure(j, self.rows[i].hash):
				f_prime = bucket.id * pow(bucket.count, self.p - 2, self.p) % self.p
				if f_prime in checked_pure:
					continue
				self.flowset[f_prime] += bucket.count
				checked_pure.add(f_prime)
				count = bucket.count
				# print(f"Found pure bucket! Flow ID: {f_prime}, Count: {bucket.count}")
				for i2, row2 in enumerate(self.rows):
					h = row2.hash(f_prime)
					row2.buckets[h].delete(f_prime, count)
		return dict(self.flowset)


