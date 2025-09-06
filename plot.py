import matplotlib.pyplot as plt

# Flow sizes you tested
flow_sizes = [40, 80, 120, 200]

# Results
traditional = [3063, 7948, 14978, 15134]
mrjittat   = [1024, 4384, 11558, 12033]
k = 2
l = 4
row = 1

# Plot
plt.figure(figsize=(8,5))
plt.plot(flow_sizes, traditional, '-o', label="Traditional Sketch")
plt.plot(flow_sizes, mrjittat, '-s', label="New Version Sketch")

# Labels and style
plt.xlabel("Flow Size (Number of Items)", fontsize=12)
plt.ylabel("Required Buckets (for ~99.9% Accuracy)", fontsize=12)
plt.title("Bucket Requirement vs Flow Size", fontsize=14)
plt.legend(loc ='upper left',title=f"k={k}, l={l}, row={row}")


plt.grid(True, linestyle="--", alpha=0.7)
plt.tight_layout()

# Show
plt.show()
