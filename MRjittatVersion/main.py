from sketch import Sketch
from collections import Counter
import random
import matplotlib.pyplot as plt
from MrJittacore import matrix_rank_finite_field,inverse_matrix
import numpy as np

debug = False

rows_cnt = 1
buckets_cnt = 1
k = 3
sketch = Sketch(rows_cnt,buckets_cnt=buckets_cnt,p= 7917,k=k,rc = 4)
flow =  [2,5,6]

for f in flow :
	sketch.insert(f)

for row in sketch.rows :
	for kbucket in row.kbuckets :
		for bucket in kbucket.buckets :
			print(bucket.count,bucket.id,end=" | ")
		print(' || ', end='')
	print()

g_original = []
for row in sketch.rows :
	for kbucket in row.kbuckets :
		for bucket in kbucket.buckets :
			g_original.append([bucket.g(f) for f in set(flow)])

print("g_original",g_original)
g = np.array(g_original, dtype=int)
print("g",g)
try :
	rank =  np.linalg.matrix_rank(g)
	print("rank",rank)
	if rank < k :
		raise Exception("Rank less than k")
	inverse_g = inverse_matrix(g)
	b = [bucket.count for row in sketch.rows for kbucket in row.kbuckets for bucket in kbucket.buckets]
	b= np.array(b, dtype=int).reshape(-1, 1)
	print("b",b)
	c = (inverse_g @ b)
	print("c",c)
	sketch.verify()
except Exception as e:
	print(e)
	inverse_g = None
