import matplotlib.pyplot as plt

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
