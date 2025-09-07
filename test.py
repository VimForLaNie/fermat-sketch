from traditional.sketch import Sketch as Sketch_Traditional
from MrjittatVersion.sketch import Sketch as Sketch_Mrjittat
import random
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import csv
import time

def calculate_flow_accuracy(flow, recovered):
    """Flow-level accuracy: fraction of distinct flows with exact count match."""
    flow_counter = Counter(flow)
    # recovered may be a dict {id: count} or a list; Counter handles both:
    recovered_counter = Counter(recovered)  # if mapping, Counter(mapping) uses mapping values
    total = len(flow_counter)
    if total == 0:
        return 1.0
    correct = sum(1 for f, c in flow_counter.items() if recovered_counter.get(f, 0) == c)
    return correct / total

def calculate_flow_exact(flow, recovered):
    """
    Trial-level exact-flow accuracy:
    Returns 1.0 only if the recovered map equals the ground-truth exactly
    (same keys and same counts). Else returns 0.0.
    """
    flow_counter = Counter(flow)
    recovered_counter = Counter(recovered)
    return 1.0 if flow_counter == recovered_counter else 0.0

def calculate_item_recall(flow, recovered):
    """Item-level recall: fraction of true items that were recovered (1 - FN_items / total_items)."""
    flow_counter = Counter(flow)         # ground truth counts
    total_items = sum(flow_counter.values())
    if total_items == 0:
        return 1.0
    missed = 0
    # recovered may be mapping or iterable; Counter(recovered) will handle mapping properly
    recovered_counter = Counter(recovered)
    for f, true_cnt in flow_counter.items():
        rec_cnt = recovered_counter.get(f, 0)
        if rec_cnt < true_cnt:
            missed += (true_cnt - rec_cnt)
    return (total_items - missed) / total_items

def mean_metric_for_config(buckets, flow_size, trials, rows, k, rc, p, flow_range, sketch_type, metric, rng, verbose=True):
    """Run `trials` experiments for a specific bucket count and return mean metric.
    metric: 'item', 'flow' (per-flow fraction), or 'flow_exact' (trial-level exact 0/1)"""
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
        elif metric == 'flow_exact':
            vals.append(calculate_flow_exact(flow, recovered))
        else:  # 'item'
            vals.append(calculate_item_recall(flow, recovered))

        # optional progress printing (disabled by default)
        # if verbose:
        #     percent = int((t + 1) * 100 / trials)
        #     print(f"\r[buckets={buckets}] Progress: {percent}% ", end="", flush=True)

    return float(np.mean(vals))

def find_min_buckets(flow_size,
                     target_acc=0.99,
                     trials=5,
                     rows=3,
                     k=2,
                     sketch_type="MrJittat",
                     metric='item',           # 'item' or 'flow' or 'flow_exact'
                     p=int(1e9+7),
                     rc=4,
                     flow_range=5000,
                     min_buckets=8,
                     max_buckets=20000,
                     seed=None,
                     verbose=False):
    """
    Find minimum bucket count (between min_buckets and max_buckets) so that
    the mean metric >= target_acc. Metric: 'item' (item-level recall),
    'flow' (per-flow fraction), or 'flow_exact' (trial-level exact match).
    Uses exponential search to find an upper bound then binary search to find minimum.
    Returns bucket count (int) or None if not found within max_buckets.
    """
    if metric not in ('item', 'flow', 'flow_exact'):
        raise ValueError("metric must be 'item', 'flow', or 'flow_exact'")

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

def run_experiment(flow_sizes, trials=5, sketch_type="MrJittat", metric='item'):
    required_buckets = []
    for flow_size in flow_sizes:
        min_buckets = find_min_buckets(flow_size, target_acc=0.99, trials=trials, sketch_type=sketch_type, metric=metric)
        required_buckets.append(min_buckets)
        print(f"Flow size {flow_size}: needs {min_buckets} buckets for {sketch_type} using metric={metric}")
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

def mean_and_std_for_config(buckets, flow_size, trials, rows, k, rc, p, flow_range, sketch_type, metric='item', seed=None, verbose=False):
    """
    Run `trials` experiments for a given bucket count and return (mean, std).
    metric: 'item', 'flow', or 'flow_exact'
    """
    if metric not in ('item', 'flow', 'flow_exact'):
        raise ValueError("metric must be 'item', 'flow' or 'flow_exact'")

    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    vals = []
    start = time.time()
    for t in range(trials):
        flow = random.choices(range(1, flow_range + 1), k=flow_size)
        if sketch_type == "Traditional":
            sketch = Sketch_Traditional(rows, buckets, p=int(p))
        else:
            sketch = Sketch_Mrjittat(rows, buckets, p=int(p), k=k, rc=rc)

        for f in flow:
            sketch.insert(f)
        recovered = sketch.verify()

        if metric == 'flow':
            vals.append(calculate_flow_accuracy(flow, recovered))
        elif metric == 'flow_exact':
            vals.append(calculate_flow_exact(flow, recovered))
        else:
            vals.append(calculate_item_recall(flow, recovered))

        if verbose:
            pct = (t + 1) * 100 // trials
            elapsed = time.time() - start
            # estimate remaining time
            avg = elapsed / (t + 1)
            remaining = avg * (trials - t - 1)
            print(f"\r  progress: {pct:3d}%  elapsed={elapsed:.1f}s  eta={remaining:.1f}s", end="", flush=True)

    if verbose:
        print("")  # newline after progress line

    # print(f" MAX VAL: {max(vals)}")
    mean_val = float(np.mean(vals)) if vals else 0.0
    std_val = float(np.std(vals, ddof=0)) if vals else 0.0
    return mean_val, std_val

def run_mean_recalls_for_buckets(bucket_counts,
                                 flow_size,
                                 trials=50,
                                 rows=1,
                                 k=2,
                                 rc=4,
                                 p=int(1e9+7),
                                 flow_range=5000,
                                 sketch_type="MrJittat",
                                 metric='item',
                                 seed=None,
                                 verbose=False,
                                 out_csv=None):
    """
    For each bucket count in bucket_counts, run trials and compute mean & std of metric.
    Returns list of tuples: [(bucket, mean, std), ...]
    metric: 'item', 'flow', 'flow_exact'
    If out_csv is provided (string), write CSV with columns: Bucket,Mean,Std
    """
    if metric not in ('item', 'flow', 'flow_exact'):
        raise ValueError("metric must be 'item', 'flow' or 'flow_exact'")

    results = []
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    total = len(bucket_counts)
    for idx, buckets in enumerate(bucket_counts):
        if verbose:
            print(f"[{idx+1}/{total}] Testing buckets={buckets} ...")
        mean_val, std_val = mean_and_std_for_config(buckets, flow_size, trials,
                                                    rows, k, rc, p, flow_range,
                                                    sketch_type, metric, seed, verbose)
        results.append((buckets, mean_val, std_val))
        if verbose:
            print(f"    -> mean={mean_val:.6f}, std={std_val:.6f}")

    # optional CSV output
    if out_csv:
        with open(out_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Bucket', f'Mean_{metric}', f'Std_{metric}'])
            for b, m, s in results:
                writer.writerow([b, f"{m:.6f}", f"{s:.6f}"])
        if verbose:
            print(f"Wrote results to {out_csv}")

    return results

def plot_mean_recalls(results, xlabel='Bucket count', ylabel='Mean item recall', title=None):
    """
    Plot results produced by run_mean_recalls_for_buckets.
    results: list of (bucket, mean, std)
    """
    buckets = [r[0] for r in results]
    means = [r[1] for r in results]
    stds = [r[2] for r in results]

    plt.figure(figsize=(8,5))
    plt.errorbar(buckets, means, yerr=stds, fmt='-o', capsize=4)
    plt.xscale('log', base=2)  # optional: log-scale makes sense for bucket sizes
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if title:
        plt.title(title)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

# Example usage (unchanged)
bucket_counts = [250, 500, 1000, 2000]  # [1000, 2000, 3000, 4000, 5000]
flow_size = 200
trials = 500
res = run_mean_recalls_for_buckets(bucket_counts,
                                   flow_size,
                                   trials=trials,
                                   rows=3,
                                   k=2,
                                   rc=4,
                                   p=int(1e9+7),
                                   flow_range=1000,
                                   sketch_type="Traditional",
                                   metric='flow_exact',   # change to 'flow_exact' to use strict trial-level exactness
                                   seed=123,
                                   verbose=True,
                                   out_csv="mean_recalls.csv")

print("Results:")
for b, m, s in res:
    print(f"buckets={b:5d} mean={m:.6f} std={s:.6f}")
for b, m, s in res:
    print(f"{m} ,", end="")

plot_mean_recalls(res, title=f"Mean metric (flow_size={flow_size}, trials={trials})")
