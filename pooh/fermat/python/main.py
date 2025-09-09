from sketch import Sketch
from collections import Counter
import random
 # ...existing code...
import argparse

debug = True
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



import time

def run_experiment(rows_cnt, buckets_cnt, element_range, max_count_per_flow, trials, p=int(1e9 + 7), verbose=False):
	success = 0
	decoding_times = []
	for t in range(trials):
		sketch = Sketch(rows_cnt, buckets_cnt, p)
		# Insert all flow IDs in the range, each with a random count between 1 and max_count_per_flow
		flow_ids = list(range(1, element_range + 1))
		elements = []
		flow_counts = {}
		for fid in flow_ids:
			cnt = random.randint(1, max_count_per_flow)
			elements.extend([fid] * cnt)
			flow_counts[fid] = cnt
		# Insert elements into sketch
		for elem in elements:
			for row in range(rows_cnt):
				sketch.rows[row].insert(elem)
		start_time = time.time()
		recovered = sketch.verify()
		end_time = time.time()
		decoding_times.append(end_time - start_time)
		fp = sum(1 for f in recovered if f not in flow_counts)
		fn = sum(1 for f in flow_counts if f not in recovered)
		if fp == 0 and fn == 0:
			# Also check counts match
			if all(recovered[f] == flow_counts[f] for f in flow_counts):
				success += 1
		if verbose and (t % max(1, trials // 10) == 0 or t == trials - 1):
			print(f"  Trial {t+1}/{trials}: Successes so far = {success}, Decoding time: {decoding_times[-1]:.6f} sec")
	mean_decoding_time = sum(decoding_times) / len(decoding_times) if decoding_times else 0.0
	return success, mean_decoding_time, decoding_times

def binary_search_buckets(rows_cnt, element_range, max_count_per_flow, required_accuracy, trials, p=int(1e9 + 7), min_buckets=1, max_buckets=100000, verbose=False):
	left = min_buckets
	right = max_buckets
	answer = None
	best_mean_time = None
	best_raw_times = None
	while left <= right:
		mid = (left + right) // 2
		print(f"Testing buckets: {mid}")
		success, mean_decoding_time, decoding_times = run_experiment(rows_cnt, mid, element_range, max_count_per_flow, trials, p, verbose=verbose)
		acc = success / trials
		print(f"Buckets: {mid}, Success: {success}/{trials}, Accuracy: {acc*100:.4f}%, Mean decoding time: {mean_decoding_time:.6f} sec")
		if acc >= required_accuracy:
			answer = mid
			best_mean_time = mean_decoding_time
			best_raw_times = decoding_times
			right = mid - 1
		else:
			left = mid + 1
	return answer, best_mean_time, best_raw_times


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="FermatSketch experiment runner")
	parser.add_argument('--rows', type=int, default=3, help='Number of rows in sketch')
	parser.add_argument('--element_range', type=int, nargs='+', default=[1000], help='List of flow ID ranges to test (e.g. 1000 2000 5000)')
	parser.add_argument('--max_count_per_flow', type=int, default=10, help='Maximum count per flow ID (each flow ID gets random count between 1 and this value)')
	parser.add_argument('--accuracy', type=float, default=99.9, help='Required accuracy in percent (e.g., 99.9)')
	parser.add_argument('--trials', type=int, default=None, help='Number of trials per experiment (default: 10x accuracy)')
	parser.add_argument('--min_buckets', type=int, default=1, help='Minimum buckets to search')
	parser.add_argument('--max_buckets', type=int, default=100000, help='Maximum buckets to search')
	parser.add_argument('--prime', type=int, default=int(1e9+7), help='Prime modulus p')
	parser.add_argument('--verbose', action='store_true', help='Print progress information during trials')
	args = parser.parse_args()

	required_accuracy = args.accuracy / 100.0
	if args.trials is not None:
		trials = args.trials
	else:
		# Linear mapping: trials = int(1000 / (1 - required_accuracy))
		if required_accuracy >= 1.0:
			trials = 1000000
		else:
			trials = int(1000 / (1 - required_accuracy))

	print(f"Running FermatSketch experiments with rows={args.rows}, accuracy={args.accuracy}%, trials={trials}")
	import csv
	results = []
	raw_time_files = []
	for element_range in args.element_range:
		print(f"\nTesting element_range={element_range}")
		min_buckets, mean_decoding_time, raw_times = binary_search_buckets(
			rows_cnt=args.rows,
			element_range=element_range,
			max_count_per_flow=args.max_count_per_flow,
			required_accuracy=required_accuracy,
			trials=trials,
			p=args.prime,
			min_buckets=args.min_buckets,
			max_buckets=args.max_buckets,
			verbose=args.verbose
		)
		if min_buckets is not None:
			print(f"Minimum buckets required for element_range={element_range} at {args.accuracy}% accuracy: {min_buckets}")
		else:
			print(f"Could not achieve required accuracy for element_range={element_range} within bucket range.")
		results.append({
			"element_range": element_range,
			"min_buckets": min_buckets if min_buckets is not None else "N/A",
			"accuracy": args.accuracy,
			"trials": trials,
			"rows": args.rows,
			"max_count_per_flow": args.max_count_per_flow,
			"mean_decoding_time": mean_decoding_time if min_buckets is not None else "N/A"
		})
		# Write raw times for this experiment
		import hashlib, time as _time, random as _random
		hash_str = hashlib.sha256(f"{_time.time()}_{_random.random()}".encode()).hexdigest()[:8]
		raw_time_filename = f"fermat_sketch_raw_times_{element_range}_{hash_str}.csv"
		with open(raw_time_filename, "w", newline="") as rawfile:
			raw_writer = csv.writer(rawfile)
			raw_writer.writerow(["trial", "decoding_time_sec"])
			for i, t in enumerate(raw_times):
				raw_writer.writerow([i+1, t])
		raw_time_files.append(raw_time_filename)

	import hashlib, time, random
	hash_str = hashlib.sha256(f"{time.time()}_{random.random()}".encode()).hexdigest()[:8]
	csv_filename = f"fermat_sketch_results_{hash_str}.csv"
	with open(csv_filename, "w", newline="") as csvfile:
		fieldnames = ["element_range", "min_buckets", "accuracy", "trials", "rows", "max_count_per_flow", "mean_decoding_time"]
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		for row in results:
			writer.writerow(row)
	print(f"\nResults written to {csv_filename}")
	print(f"Raw decoding times written to: {', '.join(raw_time_files)}")

