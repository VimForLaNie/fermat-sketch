from row import Rows
from collections import deque, defaultdict


class Sketch :
	def __init__(self, rows_cnt, buckets_cnt, p,k) :
		self.rows_cnt = rows_cnt
		self.p = p
		self.rows = [Rows(buckets_cnt, p,k) for _ in range(rows_cnt)]
		self.pure_elements = []
		self.flowset = defaultdict(int)
		self.k = k

	def verify(self):
		queue = deque()
		checked_pure = set()
		for i, row in enumerate(self.rows):
			for j, kbucket in enumerate(row.kbuckets):
				if kbucket.kbucket[0].count != 0:
					queue.append((i, j))
		
		while queue:
			i, j = queue.popleft()
			print(f"Verifying row {i}, bucket {j}")
			# kbucket = self.rows[i].kbuckets[j]
			# print(f"Processing bucket at row {i}, index {j} with count {bucket.count} and id {bucket.id}")
			k = self.rows[i].pure_verification(j)
			print("get",k)
			break
			if len(k) == 0:
				queue.append((i, j))
			else :
				print("pure",k)
				for f, cnt in k:
					for row in self.rows:
						print("delete",int(f),int(cnt))
						row.delete(f, cnt)
				self.flowset[f] += cnt
		return dict(self.flowset)

	def insert(self, f):
		for row in self.rows:
			row.insert(f)

