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
	bucket_counts = [1000, 2000, 3000, 4000, 5000]
	traditional = [0.346 ,0.662 ,0.776 ,0.842 ,0.866]
	new_sketch_l4   = [0.04409, 0.11926, 0.40447, 0.98527, 0.99915, 0.99909,0.99997,1]
	new_sketch_l3 = [0.04458 ,0.11333 ,0.31356 ,0.97483 ,0.99564 ,0.99981 ,0.9999 ,0.99999 ]
	new_sketch_l2 = [0.03638 ,0.09672 ,0.20468 ,0.93315 ,0.99136 ,0.99735 ,0.99818 ,0.99902 ,]


	k = 2
	l = 4
	row = 3

	# Plot
	plt.figure(figsize=(8,5))
	plt.plot(bucket_counts, traditional, '-o', label="Traditional Sketch")
	plt.plot(bucket_counts, new_sketch_l4, '-s', label="New Version Sketch (l = 4)")
	plt.plot(bucket_counts, new_sketch_l3, '-^', label="New Version Sketch (l = 3)")
	plt.plot(bucket_counts, new_sketch_l2, '-d', label="New Version Sketch (l = 2)")

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