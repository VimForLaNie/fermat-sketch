from sketch import Sketch
from collections import Counter
import random
import time
import csv

debug = True

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
		# Must match exactly
		return len(missing) == 0 and len(extra) == 0 and len(mismatched) == 0 and len(correct) == len(flow_counter)
	else:
		return {
			"correct": correct,
			"missing": missing,
			"extra": extra,
			"mismatched": mismatched
		}

def binary_search_min_buckets(rows_cnt, element_range, element_counts, trials, p=int(1e9 + 7), verbose=False):
	"""
	Binary search for minimum buckets needed to achieve 99% accuracy (all trials decode exactly).
	Returns min_buckets, success_rate, and decode_times.
	"""
	low = 1
	high = element_counts * 10  # Reasonable upper bound
	min_buckets = None
	best_success_rate = 0
	best_decode_times = []
	while low <= high:
		mid = (low + high) // 2
		success_count = 0
		decode_times = []
		for _ in range(trials):
			sketch = Sketch(rows_cnt, mid, p)
			elements = [i for i in range(1, element_counts + 1)]
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
		if success_rate >= 0.99:
			min_buckets = mid
			best_success_rate = success_rate
			best_decode_times = decode_times.copy()
			high = mid - 1
		else:
			low = mid + 1
	return min_buckets, best_success_rate, best_decode_times

def experiment_find_min_buckets(rows_cnt, flow_sizes, element_range, trials=5, p=int(1e9 + 7), 
								result_csv="min_buckets_results.csv", time_csv="decode_times.csv"):
	"""
	For each flow size, find minimum buckets needed for 99.9% accuracy using binary search.
	Output results to CSV files.
	"""
	# Open files in append mode, don't write headers
	with open(result_csv, "a", newline='') as f_result, open(time_csv, "a", newline='') as f_time:
		result_writer = csv.writer(f_result)
		time_writer = csv.writer(f_time)
		for flow_size in flow_sizes:
			print(f"Finding min buckets for flow_size={flow_size} ...")
			min_buckets, success_rate, decode_times = binary_search_min_buckets(
				rows_cnt, element_range, flow_size, trials, p, verbose=debug
			)
			result_writer.writerow([flow_size, min_buckets, success_rate, rows_cnt, element_range, trials])
			for idx, t in enumerate(decode_times):
				time_writer.writerow([flow_size, min_buckets, idx, t, rows_cnt, element_range, trials])
			print(f"flow_size={flow_size}, min_buckets={min_buckets}, success_rate={success_rate:.4f}")

if __name__ == "__main__":
	# Example usage:
	rows_cnt = 3
	element_ranges = [20, 40, 60, 80, 100]  # Range of possible flow IDs for each insert
	flow_size = 2000  # Number of inserts (unique flows per trial)
	trials = 5 # You can adjust this for more precision

	# Write headers only once
	result_csv = "min_buckets_results.csv"
	time_csv = "decode_times.csv"
	with open(result_csv, "w", newline='') as f_result, open(time_csv, "w", newline='') as f_time:
		result_writer = csv.writer(f_result)
		time_writer = csv.writer(f_time)
		result_writer.writerow(["flow_size", "min_buckets", "success_rate", "rows_cnt", "element_range", "trials"])
		time_writer.writerow(["flow_size", "buckets", "trial_idx", "decode_time", "rows_cnt", "element_range", "trials"])

	for element_range in element_ranges:
		print(f"Running experiment for element_range={element_range}, flow_size={flow_size}")
		experiment_find_min_buckets(
			rows_cnt, [flow_size], element_range, trials,
			result_csv=result_csv,
			time_csv=time_csv
		)
