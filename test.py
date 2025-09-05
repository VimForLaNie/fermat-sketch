from traditional.sketch import Sketch as Sketch_Traditional
from MrjittatVersion.sketch import Sketch as Sketch_Mrjittat
import random
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter


def calculate_accuracy(flow, s):
    flow_counter = Counter(flow)  # ground truth
    recovered_counter = Counter(s)

    correct = {f: flow_counter[f] for f in flow_counter if f in recovered_counter and flow_counter[f] == recovered_counter[f]}
    total_flows = len(flow_counter)

    accuracy = len(correct) / total_flows if total_flows > 0 else 0
    return accuracy


def find_min_buckets(flow_size, target_acc=0.99, trials=5, rows=1, k=2, sketch_type="MrJittat"):
    """
    Gradually increase bucket count until target accuracy is reached.
    Returns minimum bucket count required.
    """
    buckets = 10  # start small
    max_buckets = 20000

    while buckets <= max_buckets:
        accuracies = []
        for _ in range(trials):
            flow = random.choices(range(1, 5000), k=flow_size)

            if sketch_type == "Traditional":
                sketch = Sketch_Traditional(rows, buckets, p=int(1e9 + 7))
            else:
                sketch = Sketch_Mrjittat(rows, buckets, p=int(1e9 + 7), k=k, rc=12)

            for f in flow:
                sketch.insert(f)
            recovered = sketch.verify()

            acc = calculate_accuracy(flow, recovered)
            # if sketch_type == "MrJittat":
            #     print(f"Buckets: {buckets},  Accuracy: {acc:.4f}")
            accuracies.append(acc)

        mean_acc = np.mean(accuracies)
        print(f"Buckets: {buckets},  Accuracy: {mean_acc:.4f}")
        
        if mean_acc >= target_acc:
            return buckets  # found minimum bucket count

        buckets *= 2  # exponential search

    return None  # not found within range


def run_experiment(flow_sizes, trials=5, sketch_type="MrJittat"):
    required_buckets = []
    for flow_size in flow_sizes:
        min_buckets = find_min_buckets(flow_size, target_acc=0.99, trials=trials, sketch_type=sketch_type)
        required_buckets.append(min_buckets)
        print(f"Flow size {flow_size}: needs {min_buckets} buckets for {sketch_type}")
    return required_buckets


def plot_required_buckets(flow_sizes, buckets_trad, buckets_jt):
    plt.figure(figsize=(8, 5))
    plt.plot(flow_sizes, buckets_trad, '-o', label="Traditional Sketch")
    plt.plot(flow_sizes, buckets_jt, '-s', label="MrJittat Sketch")

    plt.xlabel("Victim Flow Size (Number of Items)", fontsize=12)
    plt.ylabel("Required Buckets (for ≥99.99% accuracy)", fontsize=12)
    plt.title("Bucket Requirement vs Flow Size", fontsize=14)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()


# Parameters
flow_sizes = [10, 20, 40, 80, 160]
buckets_trad = run_experiment(flow_sizes, trials=100, sketch_type="Traditional")
buckets_jt = run_experiment(flow_sizes, trials=100, sketch_type="MrJittat")

# Plot results
plot_required_buckets(flow_sizes, buckets_trad, buckets_jt)
