from sketch import Sketch
from collections import Counter
import random
import matplotlib.pyplot as plt
from MrJittacore import matrix_rank_finite_field

debug = False

rows_cnt = 1
buckets_cnt = 1
k = 3
sketch = Sketch(rows_cnt,buckets_cnt=buckets_cnt,p= 1013,k=k,rc = 4)
flow =  [1,2,2]

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
			g_original.append([bucket.g(f) for f in flow])

print("g_original",g_original)
sketch.verify()