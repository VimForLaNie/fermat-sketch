from sketch import Sketch
from collections import Counter
import random
import matplotlib.pyplot as plt

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

def experiment(rows_list, buckets_cnt, element_range, element_counts, trials=5, p=1000003):
	mean_fp_list = []
	mean_fn_list = []
	print(f"Experimenting with buckets: {buckets_cnt}, element range: {element_range}, element counts: {element_counts}, trials per row count: {trials}")

	for rows_cnt in rows_list:
		fp_trials = []
		fn_trials = []
		print(f"Running experiments for {rows_cnt} rows...")

		for _ in range(trials):
			sketch = Sketch(rows_cnt, buckets_cnt, p)

			# Generate random elements
			elements = random.choices(range(1, element_range), k=element_counts)
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

		# Compute mean for this row count
		mean_fp_list.append(sum(fp_trials) / trials)
		mean_fn_list.append(sum(fn_trials) / trials)

		if debug:
			print(f"Rows: {rows_cnt}, Mean FP: {mean_fp_list[-1]:.4f}, Mean FN: {mean_fn_list[-1]:.4f}")

	return mean_fp_list, mean_fn_list

def experiment_buckets(rows_cnt, buckets_list, element_range, element_counts, trials=5, p=int(1e9 + 7)):
	mean_fp_list = []
	mean_fn_list = []
	print(f"Experimenting with rows: {rows_cnt}, element range: {element_range}, element counts: {element_counts}, trials per bucket count: {trials}")

	for buckets_cnt in buckets_list:
		fp_trials = []
		fn_trials = []
		print(f"Running experiments for {buckets_cnt} buckets...")

		for _ in range(trials):
			sketch = Sketch(rows_cnt, buckets_cnt, p)

			# Generate random elements
			elements = random.choices(range(1, element_range), k=element_counts)
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

		# Compute mean for this bucket count
		print("success_rate : ", (element_counts - (sum(fn_trials) + sum(fp_trials))/ trials) / element_counts * 100)
		mean_fp_list.append(sum(fp_trials) / trials)
		mean_fn_list.append(sum(fn_trials) / trials)

		if debug:
			print(f"Buckets: {buckets_cnt}, Mean FP: {mean_fp_list[-1]:.4f}, Mean FN: {mean_fn_list[-1]:.4f}")

	return mean_fp_list, mean_fn_list

def experiment_element_range(rows_cnt, buckets_cnt, element_range_list, element_counts, trials=5, p=1000003):
	mean_fp_list = []
	mean_fn_list = []
	print(f"Experimenting with rows: {rows_cnt}, buckets: {buckets_cnt}, element counts: {element_counts}, trials per element range: {trials}")

	for element_range in element_range_list:
		fp_trials = []
		fn_trials = []
		print(f"Running experiments for element range: {element_range}...")

		for _ in range(trials):
			sketch = Sketch(rows_cnt, buckets_cnt, p)

			# Generate random elements
			elements = random.choices(range(1, element_range), k=element_counts)
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

		# Compute mean for this element range
		mean_fp_list.append(sum(fp_trials) / trials)
		mean_fn_list.append(sum(fn_trials) / trials)

		if debug:
			print(f"Element Range: {element_range}, Mean FP: {mean_fp_list[-1]:.4f}, Mean FN: {mean_fn_list[-1]:.4f}")

	return mean_fp_list, mean_fn_list

def plot_results_rows(rows_list, fp_list, fn_list):
	plt.figure(figsize=(10, 6))
	plt.plot(rows_list, fp_list, marker='o', label="Mean False Positive Rate")
	plt.plot(rows_list, fn_list, marker='x', label="Mean False Negative Rate")
	plt.xlabel("Number of Rows")
	plt.ylabel("Rate")
	plt.title("Mean False Positive / False Negative Rates vs. Number of Rows")
	plt.legend()
	plt.grid(True)
	plt.show()

def plot_results_buckets(buckets_list, fp_list, fn_list):
	plt.figure(figsize=(10, 6))
	plt.plot(buckets_list, fp_list, marker='o', label="Mean False Positive Rate")
	plt.plot(buckets_list, fn_list, marker='x', label="Mean False Negative Rate")
	plt.xlabel("Number of Buckets")
	plt.ylabel("Rate")
	plt.title("Mean False Positive / False Negative Rates vs. Number of Buckets")
	plt.legend()
	plt.grid(True)
	plt.show()

def plot_results_element_range(element_range_list, fp_list, fn_list):
	plt.figure(figsize=(10, 6))
	plt.plot(element_range_list, fp_list, marker='o', label="Mean False Positive Rate")
	plt.plot(element_range_list, fn_list, marker='x', label="Mean False Negative Rate")
	plt.xlabel("Element Range")
	plt.ylabel("Rate")
	plt.title("Mean False Positive / False Negative Rates vs. Element Range")
	plt.legend()
	plt.grid(True)
	plt.show()


if __name__ == "__main__":
	# rows_list = [100, 500, 1000, 1500, 2000, 2500, 3000]  # varying rows
	# # rows_list = [100,500,1000,1500,2000]
	# rows_list = [3]
	# buckets_cnt = 10000
	# # bucket_list = [ 500, 1000, 1500, 2000, 2500, 3000,4000 , 5000]  # varying buckets
	# bucket_list = [3000 * i for i in range(1, 21)]
	# element_range = 10000
	# element_range_list = [20000 * i for i in range(1, 10)]  # varying element range
	# element_counts = 5000
	# trials = 100 # number of experiments per row count

	# fp_list, fn_list = experiment_buckets(3, bucket_list, element_range, element_counts, trials)
	# fp_list, fn_list = experiment_element_range(3, 40000, element_range_list, element_counts, trials)
	# plot_results_buckets(bucket_list, fp_list, fn_list)
	# plot_results_element_range(element_range_list, fp_list, fn_list)
	rows = 2
	buckets = 100
	flow = random.choices(range(1, 100), k=100)
	sketch = Sketch(rows,buckets,p= int(1e9 + 7))
	print("flow",flow)
	for f in flow :
		sketch.insert(f)
	s = sketch.verify()
	check_flow_result(flow, s)
	# print("s",s)

