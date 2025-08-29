from traditional.sketch import Sketch as Sketch_Traditional
from MRjittatVersion.sketch import Sketch as Sketch_Mrjittat
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from data_generator import gen_data

def calculate_accuracy(flow, s):
    flow_counter = Counter(flow)  # ground truth
    recovered_counter = Counter(s)

    missing = {f: flow_counter[f] for f in flow_counter if f not in recovered_counter}
    extra = {f: recovered_counter[f] for f in recovered_counter if f not in flow_counter}
    mismatched = {f: (flow_counter[f], recovered_counter[f])
                  for f in flow_counter if f in recovered_counter and flow_counter[f] != recovered_counter[f]}
    correct = {f: flow_counter[f] for f in flow_counter if f in recovered_counter and flow_counter[f] == recovered_counter[f]}

    false_negatives = len(missing) + len(mismatched)
    false_positives = len(extra)
    total_flows = len(flow_counter)

    fn_rate = false_negatives / total_flows if total_flows > 0 else 0
    fp_rate = false_positives / (false_positives + len(correct)) if (false_positives + len(correct)) > 0 else 0
    accuracy = len(correct) / total_flows if total_flows > 0 else 0

    return accuracy, fn_rate, fp_rate

def run_experiment(flow_id_ranges, victim_flow_ratio=0.2, packet_loss_rate=0.1, packets_per_flow=10000, 
                  trials=5, trad_rows=3, trad_buckets=500, mrjittat_rows=3, mrjittat_buckets=500, 
                  mrjittat_k=2):
    results = {"Traditional": {"acc": [], "fn": [], "fp": []},
               "MrJittat": {"acc": [], "fn": [], "fp": []}}

    for flow_id_range in flow_id_ranges:
        acc1, fn1, fp1 = [], [], []
        acc2, fn2, fp2 = [], [], []

        for _ in range(trials):
            flow = gen_data(flow_id_range, victim_flow_ratio, packet_loss_rate, packets_per_flow)

            sketch_trad = Sketch_Traditional(trad_rows, trad_buckets, p=int(1e9 + 7))
            sketch_jt = Sketch_Mrjittat(1, mrjittat_buckets, p=int(1e9 + 7), k=mrjittat_k, rc=mrjittat_rows)

            for f in flow:
                sketch_trad.insert(f)
                sketch_jt.insert(f)

            s1 = sketch_trad.verify()
            s2 = sketch_jt.verify()

            a1, fnr1, fpr1 = calculate_accuracy(flow, s1)
            a2, fnr2, fpr2 = calculate_accuracy(flow, s2)

            acc1.append(a1)
            fn1.append(fnr1)
            fp1.append(fpr1)

            acc2.append(a2)
            fn2.append(fnr2)
            fp2.append(fpr2)

        # average + std for error bars
        results["Traditional"]["acc"].append((np.mean(acc1), np.std(acc1)))
        results["Traditional"]["fn"].append((np.mean(fn1), np.std(fn1)))
        results["Traditional"]["fp"].append((np.mean(fp1), np.std(fp1)))

        results["MrJittat"]["acc"].append((np.mean(acc2), np.std(acc2)))
        results["MrJittat"]["fn"].append((np.mean(fn2), np.std(fn2)))
        results["MrJittat"]["fp"].append((np.mean(fp2), np.std(fp2)))

    return results

def plot_results(flow_id_ranges, results, metric="acc"):
    plt.figure(figsize=(10, 6))

    means1 = [m for m, _ in results["Traditional"][metric]]
    stds1 = [s for _, s in results["Traditional"][metric]]
    means2 = [m for m, _ in results["MrJittat"][metric]]
    stds2 = [s for _, s in results["MrJittat"][metric]]

    plt.errorbar(flow_id_ranges, means1, yerr=stds1, fmt='-o', capsize=4, label="Traditional Sketch")
    plt.errorbar(flow_id_ranges, means2, yerr=stds2, fmt='-s', capsize=4, label="MrJittat Sketch")

    ylabel_map = {"acc": "Accuracy", "fn": "False Negative Rate", "fp": "False Positive Rate"}
    plt.xlabel("Flow ID Range", fontsize=12)
    plt.ylabel(ylabel_map[metric], fontsize=12)
    plt.title(f"Comparison of {ylabel_map[metric]} vs Flow ID Range", fontsize=14)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()

# Sketch sizing parameters
SKETCH_CONFIG = {
    'trad_rows': 3,
    'trad_buckets': 500,
    'mrjittat_rows': 3,
    'mrjittat_buckets': 500,
    'mrjittat_k': 2
}

# Data generation parameters
DATA_CONFIG = {
    'victim_flow_ratio': 0.2,
    'packet_loss_rate': 0.1,
    'packets_per_flow': 10000,
    'trials': 5
}

# Parameters
flow_id_ranges = [1000, 2000, 3000, 4000, 5000]
results = run_experiment(
    flow_id_ranges=flow_id_ranges,
    **DATA_CONFIG,
    **SKETCH_CONFIG
)

# Plot all metrics
for metric in ["acc", "fn", "fp"]:
    plot_results(flow_id_ranges, results, metric)
