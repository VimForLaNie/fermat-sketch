from traditional.sketch import Sketch as Sketch_Traditional
from MrjittatVersion.sketch import Sketch as Sketch_Mrjittat
import random
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

def calculate_flow_accuracy(flow, recovered):
    """Flow-level accuracy: fraction of distinct flows with exact count match."""
    flow_counter = Counter(flow)
    recovered_counter = Counter(recovered)
    total = len(flow_counter)
    if total == 0:
        return 1.0
    correct = sum(1 for f,c in flow_counter.items() if recovered_counter.get(f,0) == c)
    return correct / total

def calculate_item_recall(flow, recovered):
    """Item-level recall: fraction of true items that were recovered (1 - FN_items / total_items)."""
    flow_counter = Counter(flow)         # ground truth counts
    total_items = sum(flow_counter.values())
    if total_items == 0:
        return 1.0
    missed = 0
    for f, true_cnt in flow_counter.items():
        rec_cnt = recovered.get(f, 0)
        if rec_cnt < true_cnt:
            missed += (true_cnt - rec_cnt)
    # recall = (total_items - missed) / total_items
    # print(f"Total items: {total_items}, Missed items: {missed}, Recall: {(total_items - missed) / total_items:.4f}")
    return (total_items - missed) / total_items

def mean_metric_for_config(buckets, flow_size, trials, rows, k, rc, p, flow_range, sketch_type, metric, rng, verbose=True):
    """Run `trials` experiments for a specific bucket count and return mean metric."""
    vals = []
    for t in range(trials):
        flow = random.choices(range(1, flow_range + 1), k=flow_size)
        if sketch_type == "Traditional":
            sketch = Sketch_Traditional(rows, buckets, p=int(p))
        else:
            sketch = Sketch_Mrjittat(rows, buckets, p=int(p), k=k, rc=rc)

        for f in flow:
            sketch.insert(f)
        recovered = sketch.verify()  # expected dict: {flow_id: count, ...}

        if metric == 'flow':
            vals.append(calculate_flow_accuracy(flow, recovered))
        else:  # 'item'
            vals.append(calculate_item_recall(flow, recovered))

        # ---- Progress bar ----
        # if verbose:
            # percent = int((t + 1) * 100 / trials)
            # print(f"\r[buckets={buckets}] Progress: {percent}% ", end="", flush=True)

    # if verbose:
        # print("")  # newline after finishing
    return float(np.mean(vals))

def find_min_buckets(flow_size,
                     target_acc=0.99,
                     trials=5,
                     rows=3,
                     k=2,
                     sketch_type="MrJittat",
                     metric='item',           # 'item' or 'flow'
                     p=int(1e9+7),
                     rc=4,
                     flow_range=5000,
                     min_buckets=8,
                     max_buckets=20000,
                     seed=None,
                     verbose=False):
    """
    Find minimum bucket count (between min_buckets and max_buckets) so that
    the mean metric >= target_acc. Metric: 'item' (item-level recall) or 'flow' (flow-level exact match).
    Uses exponential search to find an upper bound then binary search to find minimum.
    Returns bucket count (int) or None if not found within max_buckets.
    """
    if metric not in ('item', 'flow'):
        raise ValueError("metric must be 'item' or 'flow'")

    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    # quick check at min_buckets
    low = max(1, int(min_buckets))
    high = low
    mean_at_low = mean_metric_for_config(low, flow_size, trials, rows, k, rc, p, flow_range, sketch_type, metric, random)
    if verbose:
        print(f"[check] buckets={low}, mean_{metric}={mean_at_low:.6f}")
    if mean_at_low >= target_acc:
        return low

    # exponential search to find high such that mean >= target_acc or until max_buckets
    while high <= max_buckets:
        high = min(high * 2, max_buckets)
        mean_high = mean_metric_for_config(high, flow_size, trials, rows, k, rc, p, flow_range, sketch_type, metric, random)
        if verbose:
            print(f"[exp] buckets={high}, mean_{metric}={mean_high:.6f}")
        if mean_high >= target_acc:
            break
        if high == max_buckets:
            # not found
            if verbose:
                print(f"Not found up to max_buckets={max_buckets}")
            return None

    # now binary search between low and high (we know low < target, high >= target)
    left, right = low, high
    while left < right:
        mid = left + (right - left) // 2
        mean_mid = mean_metric_for_config(mid, flow_size, trials, rows, k, rc, p, flow_range, sketch_type, metric, random)
        if verbose:
            print(f"[bin] mid={mid}, mean_{metric}={mean_mid:.6f}")
        if mean_mid >= target_acc:
            right = mid
        else:
            left = mid + 1

    # final check
    final_mean = mean_metric_for_config(left, flow_size, trials, rows, k, rc, p, flow_range, sketch_type, metric, random)
    print(f"[final] buckets={left}, mean_{metric}={final_mean:.6f}")
    return left



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
flow_sizes = [ 40, 80, 120, 200]
buckets_trad = run_experiment(flow_sizes, trials=500, sketch_type="Traditional")
# buckets_jt = run_experiment(flow_sizes, trials=100, sketch_type="MrJittat")

# Plot results
# plot_required_buckets(flow_sizes, buckets_trad, buckets_jt)
