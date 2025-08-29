from sketch import Sketch
from collections import Counter
import random
import matplotlib.pyplot as plt
import numpy as np

def check_flow_result(flow, s, verbose=True):
    """
    Compare flow list with the recovered flowset dictionary and print summary.
    """
    flow_counter = Counter(flow)  # ground truth
    recovered_counter = Counter(s)

    missing = {f: flow_counter[f] for f in flow_counter if f not in recovered_counter}
    extra = {f: recovered_counter[f] for f in recovered_counter if f not in flow_counter}
    mismatched = {f: (flow_counter[f], recovered_counter[f])
                  for f in flow_counter if f in recovered_counter and flow_counter[f] != recovered_counter[f]}
    correct = {f: flow_counter[f] for f in flow_counter if f in recovered_counter and flow_counter[f] == recovered_counter[f]}

    if verbose:
        print("=== Flow Verification ===")
        print("Inserted flows:", dict(flow_counter))
        print("Recovered flows:", dict(recovered_counter))
        print()

        if correct:
            print("✅ Correct:")
            for f, c in correct.items():
                print(f"   Flow {f}: count = {c}")
        if missing:
            print("❌ Missing:")
            for f, c in missing.items():
                print(f"   Flow {f}: expected {c}, got 0")
        if mismatched:
            print("⚠️ Mismatched:")
            for f, (exp, got) in mismatched.items():
                print(f"   Flow {f}: expected {exp}, got {got}")
        if extra:
            print("➕ Extra (not in flow but appeared in s):")
            for f, c in extra.items():
                print(f"   Flow {f}: got {c}")
        print("=========================")

    return {
        "correct": correct,
        "missing": missing,
        "extra": extra,
        "mismatched": mismatched
    }


debug = False

rows_cnt = 1
buckets_cnt = 100
sketch = Sketch(rows_cnt,buckets_cnt=buckets_cnt,p= int(1e9 + 7),k=2,rc = 3)
flow =  random.choices(range(1, 100), k=100)
print("flow",flow)

for f in flow :
	sketch.insert(f)

# for row in sketch.rows :
# 	for kbucket in row.kbuckets :
# 		for bucket in kbucket.buckets :
# 			print(bucket.count,bucket.id,end=" | ")
# 		print(' || ', end='')
# 	print()

g_original = []
for row in sketch.rows :
	for kbucket in row.kbuckets :
		for i,bucket in enumerate(kbucket.buckets) :
			g_original.append([bucket.g(f,i) for f in set(flow)])

# print("g_original",g_original)
g = np.array(g_original, dtype=int)
# print("g",g)
try :
	rank =  np.linalg.matrix_rank(g)
	# print("rank",rank)
	# if rank < k :
	# 	raise Exception("Rank less than k")
	# inverse_g = inverse_matrix(g)
	# b = [bucket.count for row in sketch.rows for kbucket in row.kbuckets for bucket in kbucket.buckets]
	# b= np.array(b, dtype=int).reshape(-1, 1)
	# print("b",b)
	# c = (inverse_g @ b)
	# print("c",c)
	s = sketch.verify()
	# print("s",s)
	check_flow_result(flow, s)
except Exception as e:
	print(e)
	inverse_g = None


