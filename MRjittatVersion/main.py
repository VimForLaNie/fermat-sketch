from sketch import Sketch
from collections import Counter
import random
import matplotlib.pyplot as plt
from MrJittacore import matrix_rank_finite_field

debug = False

rows_cnt = 1
buckets_cnt = 1
k = 3
sketch = Sketch(rows_cnt,buckets_cnt=buckets_cnt,p= 1013,k=k)
flow =  [1,2,3]
for f in flow :
	sketch.insert(f)

for row in sketch.rows :
	for kbucket in row.kbuckets :
		for bucket in kbucket.kbucket :
			print(bucket.count,bucket.id,end=" | ")
		print(' || ', end='')
	print()

sketch.verify()