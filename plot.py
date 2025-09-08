import matplotlib.pyplot as plt


def plot_bucket_requirements():
# Flow sizes you tested
	flow_sizes = [40, 80, 120]

	# Results
	traditional = [15282, 24561, 32339]
	new_version_sketch_l4   = [1542, 3977, 10581]
	new_version_sketch_l2 = [4006,12362,19590]
	new_version_sketch_l6 = [182,847,2048]
	k = 2
	row = 3

	# Plot
	plt.figure(figsize=(8,5))
	plt.plot(flow_sizes, traditional, '-o', label="Traditional Sketch")
	plt.plot(flow_sizes, new_version_sketch_l4, '-s', label="New Version Sketch (l = 4)")
	plt.plot(flow_sizes, new_version_sketch_l2, '-^', label="New Version Sketch (l = 2)")

	# Labels and style
	plt.xlabel("Flow Size (Number of Items)", fontsize=12)
	plt.ylabel("Required Buckets (for ~99% Accuracy)", fontsize=12)
	plt.title("Bucket Requirement vs Flow Size", fontsize=14)
	plt.legend(loc ='upper left',title=f"k={k}, d={row}, trials=500")


	plt.grid(True, linestyle="--", alpha=0.7)
	plt.tight_layout()

	# Show
	plt.show()


def plot_recall_vs_buckets():
	# Flow size
	flow_size = 120

	# Results
	bucket_counts = [250, 500, 1000, 2000]
	traditional = [0.0 ,0.102 ,0.538 ,0.778 ]
	# new_sketch_l4   = [0.804 ,0.916 ,0.964 ,0.974 ,]
	new_sketch_l4   = [0.49 ,0.644 ,0.81 ,0.888 ,]
	# new_sketch_l5 = [0.85 ,0.944 ,0.978 ,0.986 ,]
	new_sketch_l5 = [0.56 ,0.74 ,0.878 ,0.932 ,]
	# new_sketch_l8 = [0.916 ,0.976 ,0.978 ,0.99 ]
	new_sketch_l8 = [0.758 ,0.884 ,0.932 ,0.964 ]


	k = 2
	row = 3

	# Plot
	plt.figure(figsize=(5,5))
	plt.plot(bucket_counts, traditional, '-o', label="FermatSketch",fillstyle='none')
	plt.plot(bucket_counts, new_sketch_l4, '-s', label="L = 4",fillstyle='none')
	plt.plot(bucket_counts, new_sketch_l5, '-^', label="L = 5",fillstyle='none')
	plt.plot(bucket_counts, new_sketch_l8, '-v', label="L = 8",fillstyle='none')

	# Labels and style
	plt.xlabel("Total number of slots", fontsize=12)
	plt.ylabel("Extraction success probability", fontsize=12)
	# plt.title(f"Accuracy vs Number of Buckets (Flow Size={flow_size})", fontsize=14)
	# plt.legend(loc ='lower right',title=f"k={k},  d={row}, trials=500")
	plt.legend()
	plt.ylim(-0.05,1)

	# plt.grid(True, linestyle="--", alpha=0.7)
	plt.tight_layout()

	# Show
	plt.show()


# plot_recall_vs_buckets()
plot_bucket_requirements()