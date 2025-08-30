from collections import deque, defaultdict
from row import Rows


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


