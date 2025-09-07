import matplotlib.pyplot as plt


def plot_bucket_requirements():
# Flow sizes you tested
	flow_sizes = [40, 80, 120]

	# Results
	traditional = [77, 153, 229]
	mrjittat   = [12, 22, 31]
	k = 2
	l = 4
	row = 3

	# Plot
	plt.figure(figsize=(8,5))
	plt.plot(flow_sizes, traditional, '-o', label="Traditional Sketch")
	plt.plot(flow_sizes, mrjittat, '-s', label="New Version Sketch")

	# Labels and style
	plt.xlabel("Flow Size (Number of Items)", fontsize=12)
	plt.ylabel("Required Buckets (for ~99% Accuracy)", fontsize=12)
	plt.title("Bucket Requirement vs Flow Size", fontsize=14)
	plt.legend(loc ='upper left',title=f"k={k}, l={l}, d={row}, trials=500")


	plt.grid(True, linestyle="--", alpha=0.7)
	plt.tight_layout()

	# Show
	plt.show()


def plot_recall_vs_buckets():
	# Flow size
	flow_size = 200

	# Results
	bucket_counts = [250, 500, 1000, 2000]
	traditional = [0.0 ,0.016 ,0.346 ,0.662 ]
	new_sketch_l4   = [0 ,0.136 ,0.516 ,0.756 ,]
	new_sketch_l5 = [0 ,0.176 ,0.576 ,0.796 ,]

	k = 2
	l = 4
	row = 3

	# Plot
	plt.figure(figsize=(8,5))
	plt.plot(bucket_counts, traditional, '-o', label="Traditional Sketch")
	plt.plot(bucket_counts, new_sketch_l4, '-s', label="New Version Sketch (l = 4)")

	# Labels and style
	plt.xlabel("Number of Buckets", fontsize=12)
	plt.ylabel("Recall", fontsize=12)
	plt.title(f"Recall vs Number of Buckets (Flow Size={flow_size})", fontsize=14)
	plt.legend(loc ='lower right',title=f"k={k},  d={row}, trials=500")
	plt.ylim(0,1)

	plt.grid(True, linestyle="--", alpha=0.7)
	plt.tight_layout()

	# Show
	plt.show()


plot_recall_vs_buckets()