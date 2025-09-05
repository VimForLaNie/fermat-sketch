from sketch import Sketch
from collections import Counter
import random
import matplotlib.pyplot as plt
import numpy as np

def experiment_buckets(rows_cnt, buckets_list, element_range, element_counts, trials=5, p=int(1e9 + 7)):
	mean_fp_list = []
	mean_fn_list = []
	mean_acc_list = []
	print(f"Experimenting with rows: {rows_cnt}, element range: {element_range}, element counts: {element_counts}, trials per bucket count: {trials}")

	for buckets_cnt in buckets_list:
		fp_trials = []
		fn_trials = []
		acc_trials = []
		print(f"Running experiments for {buckets_cnt} buckets...")

		for _ in range(trials):
			# print("trial:",_ )
			sketch = Sketch(rows_cnt, buckets_cnt, p, k=2,rc =10)

			# Generate random elements
			# elements = random.sample(range(1, element_range), k=element_counts)
			elements = [i for i in range(1,element_counts + 1)]
			original_counts = Counter(elements)

			# Insert elements into sketch
			for elem in elements:
				for row in range(rows_cnt):
					sketch.rows[row].insert(elem)

			# Recover flow counts
			recovered = sketch.verify()

			# Calculate false positives and false negatives
			fp = sum(1 for f in recovered if f not in original_counts)
			fn = sum(1 for f in original_counts if f not in recovered)

			# fp_trials.append(fp / len(original_counts))  # normalized
			fp_trials.append(fp )
			
			fn_trials.append(fn )
			# fn_trials.append(fn / len(original_counts))  # normalized
			acc = (element_counts - (fn + fp)) / element_counts * 100
			acc_trials.append(acc)

		# Compute mean for this bucket count
		print("success_rate : ", (element_counts - (sum(fn_trials) + sum(fp_trials))/ trials) / element_counts * 100)
		mean_fp_list.append(sum(fp_trials) / trials)
		mean_fn_list.append(sum(fn_trials) / trials)
		mean_acc_list.append(sum(acc_trials) / trials)

		if debug:
			print(f"Buckets: {buckets_cnt}, Mean FP: {mean_fp_list[-1]:.4f}, Mean FN: {mean_fn_list[-1]:.4f}")

	return mean_fp_list, mean_fn_list, mean_acc_list


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

def plot_results_buckets(buckets_list, fp_list, fn_list,acc):
	plt.figure(figsize=(10, 6))
	# plt.plot(buckets_list, fp_list, marker='o', label="Mean False Positive Rate")
	# plt.plot(buckets_list, fn_list, marker='x', label="Mean False Negative Rate")
	plt.plot(buckets_list, acc, marker='o', label="Accuracy Rate")
	plt.xlabel("Number of Buckets")
	plt.ylabel("Rate")
	# plt.title("Mean False Positive / False Negative Rates vs. Number of Buckets")
	plt.title("Accuracy Rate vs. Number of Buckets")
	plt.legend()
	plt.grid(True)
	plt.show()

debug = False
bucket_list = [100 * i for i in range(1, 5)]
element_range = 10000
element_counts = 100
trials = 5
fp_list, fn_list ,acc = experiment_buckets(2, bucket_list, element_range, element_counts, trials)
plot_results_buckets(bucket_list, fp_list, fn_list,acc)

# rows_cnt = 1
# buckets_cnt = 100
# sketch = Sketch(rows_cnt,buckets_cnt=buckets_cnt,p= int(1e9 + 7),k=2,rc = 3)
# flow =  random.choices(range(1, 100), k=100)
# print("flow",flow)

# for f in flow :
# 	sketch.insert(f)

# for row in sketch.rows :
# 	for kbucket in row.kbuckets :
# 		for bucket in kbucket.buckets :
# 			print(bucket.count,bucket.id,end=" | ")
# 		print(' || ', end='')
# 	print()

# g_original = []
# for row in sketch.rows :
# 	for kbucket in row.kbuckets :
# 		for i,bucket in enumerate(kbucket.buckets) :
# 			g_original.append([bucket.g(f,i) for f in set(flow)])

# # print("g_original",g_original)
# g = np.array(g_original, dtype=int)
# # print("g",g)
# try :
# 	rank =  np.linalg.matrix_rank(g)
# 	# print("rank",rank)
# 	# if rank < k :
# 	# 	raise Exception("Rank less than k")
# 	# inverse_g = inverse_matrix(g)
# 	# b = [bucket.count for row in sketch.rows for kbucket in row.kbuckets for bucket in kbucket.buckets]
# 	# b= np.array(b, dtype=int).reshape(-1, 1)
# 	# print("b",b)
# 	# c = (inverse_g @ b)
# 	# print("c",c)
# 	s = sketch.verify()
# 	# print("s",s)
# 	check_flow_result(flow, s)
# except Exception as e:
# 	print(e)
# 	inverse_g = None


