import random
import numpy as np

p = int(1e9 + 7)
rc = 3
prime = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
prime = [[prime[i + j * rc] for i in range(rc)] for j in range(rc)]
k = 2
# trial = 
# for 
flow = [random.randint(1,1000) for _ in range(k)]
a = [random.randint(1, p - 1) for _ in range(k)]
b = [random.randint(0, p - 1) for _ in range(k)]
g = [[prime[_][((a[_] * flow[i] + b[_]) %p ) %rc ] for i in range(k)] for _ in range(k)]
rank = np.linalg.matrix_rank(g)
print("flow",flow)
print("g",g)
print("rank",rank)