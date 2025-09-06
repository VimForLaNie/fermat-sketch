from sketch import Sketch
from collections import Counter
import random
import numpy as np
import time
import csv

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

	return mean_fp_list, mean_fn_list, mean_acc_list


def check_flow_result(flow, s, strict=True, verbose=True):
	"""
	Compare flow list with the recovered flowset dictionary and print summary.
	If strict=True, returns True only if recovered matches ground truth exactly.
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

	if strict:
		return len(missing) == 0 and len(extra) == 0 and len(mismatched) == 0 and len(correct) == len(flow_counter)
	else:
		return {
			"correct": correct,
			"missing": missing,
			"extra": extra,
			"mismatched": mismatched
		}

def binary_search_min_buckets(rows_cnt, element_range, element_counts, trials, p=int(1e9 + 7), k=2, rc=10, verbose=False):
	low = 1
	high = element_counts * 10
	min_buckets = None
	best_success_rate = 0
	best_decode_times = []
	while low <= high:
		mid = (low + high) // 2
		success_count = 0
		decode_times = []
		for _ in range(trials):
			sketch = Sketch(rows_cnt, mid, p, k=k, rc=rc)
			elements = [random.randint(1, element_range) for _ in range(element_counts)]
			original_counts = Counter(elements)
			for elem in elements:
				for row in range(rows_cnt):
					sketch.rows[row].insert(elem)
			start = time.time()
			recovered = sketch.verify()
			end = time.time()
			decode_times.append(end - start)
			if check_flow_result(elements, recovered, strict=True, verbose=False):
				success_count += 1
		success_rate = success_count / trials
		if verbose:
			print(f"Buckets: {mid}, Success rate: {success_rate:.4f}")
		if success_rate >= 0.999:
			min_buckets = mid
			best_success_rate = success_rate
			best_decode_times = decode_times.copy()
			high = mid - 1
		else:
			low = mid + 1
	return min_buckets, best_success_rate, best_decode_times

def experiment_find_min_buckets(rows_cnt, element_counts, element_range, trials=5, p=int(1e9 + 7), k=2, rc=20,
								result_csv="min_buckets_results.csv", time_csv="decode_times.csv"):
	# Open files in append mode, don't write headers
	with open(result_csv, "a", newline='') as f_result, open(time_csv, "a", newline='') as f_time:
		result_writer = csv.writer(f_result)
		time_writer = csv.writer(f_time)
		print(f"Finding min buckets for element_range={element_range} ...")
		min_buckets, success_rate, decode_times = binary_search_min_buckets(
			rows_cnt, element_range, element_counts, trials, p, k, rc, verbose=False
		)
		result_writer.writerow([element_counts, min_buckets, success_rate, rows_cnt, element_range, trials, k, rc])
		for idx, t in enumerate(decode_times):
			time_writer.writerow([element_counts, min_buckets, idx, t, rows_cnt, element_range, trials, k, rc])
		print(f"element_counts={element_counts}, min_buckets={min_buckets}, success_rate={success_rate:.4f}")

# debug = False
# bucket_list = [100 * i for i in range(1, 5)]
# element_range = 10000
# element_counts = 100
# trials = 5
# fp_list, fn_list ,acc = experiment_buckets(2, bucket_list, element_range, element_counts, trials)

if __name__ == "__main__":
	rows_cnt = 3
	element_ranges = [50, 100, 150, 200, 250, 300]  # Range of possible flow IDs for each insert
	element_counts = 6000
	trials = 1000

	# Use single result and time file for all ranges
	result_csv = "min_buckets_results.csv"
	time_csv = "decode_times.csv"

	# Write headers only once
	with open(result_csv, "w", newline='') as f_result, open(time_csv, "w", newline='') as f_time:
		result_writer = csv.writer(f_result)
		time_writer = csv.writer(f_time)


	for element_range in element_ranges:
		print(f"Running experiment for element_range={element_range}")
		# Open files in append mode for each run
		experiment_find_min_buckets(
			rows_cnt, element_counts, element_range, trials,
			result_csv=result_csv,
			time_csv=time_csv
		)