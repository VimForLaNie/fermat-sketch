from row import Rows
from collections import deque, defaultdict
import numpy as np


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

