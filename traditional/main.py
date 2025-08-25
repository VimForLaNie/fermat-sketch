from sketch import Sketch
from collections import Counter
import random
import matplotlib.pyplot as plt

debug = False

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

def plot_results(rows_list, fp_list, fn_list):
	plt.figure(figsize=(10, 6))
	plt.plot(rows_list, fp_list, marker='o', label="Mean False Positive Rate")
	plt.plot(rows_list, fn_list, marker='x', label="Mean False Negative Rate")
	plt.xlabel("Number of Rows")
	plt.ylabel("Rate")
	plt.title("Mean False Positive / False Negative Rates vs. Number of Rows")
	plt.legend()
	plt.grid(True)
	plt.show()

if __name__ == "__main__":
	# rows_list = [100, 500, 1000, 1500, 2000, 2500, 3000]  # varying rows
	rows_list = [100,500,1000,1500,2000]
	buckets_cnt = 750
	element_range = 1000
	element_counts = 500
	trials = 3  # number of experiments per row count

	fp_list, fn_list = experiment(rows_list, buckets_cnt, element_range, element_counts, trials)
	plot_results(rows_list, fp_list, fn_list)
