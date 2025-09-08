#pragma once

#include <vector>
#include <random>
#include <unordered_map>
#include <iostream>
#include <fstream>
#include <chrono>
#include <iomanip>
#include <limits>
#include "./sketch.h"

// Compute strict exact flow accuracy for one trial
static double compute_exact_flow_accuracy(Sketch &sketch, const std::vector<int> &flow_events)
{
	std::unordered_map<long long, int> truth;
	for (int f : flow_events)
		truth[f]++;

	auto recovered = sketch.verify();
	return (truth == recovered) ? 1.0 : 0.0;
}

// Measure per-trial wallclock times and compute exact accuracy
static std::vector<double> measure_trial_times_and_accuracy(int rows_cnt,
															int buckets_cnt,
															long long p,
															int k,
															int rc,
															int inserts_per_trial,
															int trials,
															int flow_id_min,
															int flow_id_max,
															std::mt19937 &rng)
{
	std::uniform_int_distribution<int> dist_flow(flow_id_min, flow_id_max);
	std::vector<double> accuracies;
	accuracies.reserve(trials);

	for (int t = 0; t < trials; ++t)
	{
		Sketch sketch(rows_cnt, buckets_cnt, p, k, rc);
		std::vector<int> events;
		events.reserve(inserts_per_trial);

		auto t0 = std::chrono::high_resolution_clock::now();

		for (int i = 0; i < inserts_per_trial; ++i)
		{
			int f = dist_flow(rng);
			events.push_back(f);
			sketch.insert(f);
		}

		// compute exact flow accuracy
		double acc = compute_exact_flow_accuracy(sketch, events);
		accuracies.push_back(acc);

		auto t1 = std::chrono::high_resolution_clock::now();
		std::chrono::duration<double> elapsed = t1 - t0;
		// store elapsed time in place of accuracy if needed for CSV
		// we can write both later
	}

	return accuracies;
}

// Find minimal bucket count for each insert count to reach target exact flow accuracy
static std::vector<int> find_min_buckets_for_insert_counts(
	const std::vector<int> &insert_counts,
	double target_accuracy = 0.999,
	int trials = 5,
	int rows_cnt = 1,
	int k = 2,
	int rc = 4,
	long long p = 1000000007LL,
	int flow_id_min = 1,
	int flow_id_max = 1000,
	int min_buckets = 8,
	int max_buckets = 1 << 20)
{
	std::random_device rd;
	std::mt19937 rng(rd());

	std::vector<int> result;
	result.reserve(insert_counts.size());

	// Prepare times matrix: rows = trials, cols = insert_counts.size()
	std::cout << "Finding minimal buckets for insert counts: k = " << k << ", rc = " << rc << ", rows = " << rows_cnt << ", p = " << p << "\n";
	size_t C = insert_counts.size();
	std::vector<std::vector<double>> times_matrix(static_cast<size_t>(trials), std::vector<double>(C, std::numeric_limits<double>::quiet_NaN()));

	for (size_t ci = 0; ci < insert_counts.size(); ++ci)
	{
		int inserts = insert_counts[ci];

		int low = min_buckets;
		int high = low;
		int found_bucket = -1;

		// quick check at low
		double mean_acc = 0.0;
		{
			auto accs = measure_trial_times_and_accuracy(rows_cnt, high, p, k, rc, inserts, trials, flow_id_min, flow_id_max, rng);
			mean_acc = std::accumulate(accs.begin(), accs.end(), 0.0) / static_cast<double>(accs.size());
			for (int t = 0; t < trials; ++t)
				times_matrix[static_cast<size_t>(t)][ci] = accs[static_cast<size_t>(t)];
		}

		if (mean_acc >= target_accuracy)
		{
			found_bucket = high;
		}
		else
		{
			while (high <= max_buckets)
			{
				high *= 2;
				if (high > max_buckets)
					high = max_buckets;

				auto accs = measure_trial_times_and_accuracy(rows_cnt, high, p, k, rc, inserts, trials, flow_id_min, flow_id_max, rng);
				mean_acc = std::accumulate(accs.begin(), accs.end(), 0.0) / static_cast<double>(accs.size());
				for (int t = 0; t < trials; ++t)
					times_matrix[static_cast<size_t>(t)][ci] = accs[static_cast<size_t>(t)];

				if (mean_acc >= target_accuracy)
				{
					found_bucket = high;
					break;
				}

				if (high == max_buckets)
					break;
			}
		}

		if (found_bucket == -1)
		{
			result.push_back(-1);
			std::cout << "Inserts " << inserts << ": NOT found up to max_buckets=" << max_buckets << "\n";
			continue;
		}

		// binary search between low and found_bucket
		int left = min_buckets;
		int right = found_bucket;
		while (left < right)
		{
			int mid = left + (right - left) / 2;
			auto accs = measure_trial_times_and_accuracy(rows_cnt, mid, p, k, rc, inserts, trials, flow_id_min, flow_id_max, rng);
			double acc_mid = std::accumulate(accs.begin(), accs.end(), 0.0) / static_cast<double>(accs.size());
			for (int t = 0; t < trials; ++t)
				times_matrix[static_cast<size_t>(t)][ci] = accs[static_cast<size_t>(t)];

			if (acc_mid >= target_accuracy)
				right = mid;
			else
				left = mid + 1;
		}

		result.push_back(left);
		std::cout << "Inserts " << inserts << ": required buckets = " << left
				  << " (target accuracy=" << target_accuracy << ")\n";
	}

	// Write CSV file "timings.csv"
	std::ofstream out("timings.csv");
	if (!out)
	{
		std::cerr << "Failed to open timings.csv for writing\n";
	}
	else
	{
		// header
		for (size_t ci = 0; ci < insert_counts.size(); ++ci)
		{
			out << "inserts_" << insert_counts[ci];
			if (ci + 1 < insert_counts.size())
				out << ',';
		}
		out << '\n';

		// rows: each trial
		for (int t = 0; t < trials; ++t)
		{
			for (size_t ci = 0; ci < insert_counts.size(); ++ci)
			{
				double v = times_matrix[static_cast<size_t>(t)][ci];
				if (std::isnan(v))
					out << "";
				else
					out << std::fixed << std::setprecision(6) << v;
				if (ci + 1 < insert_counts.size())
					out << ',';
			}
			out << '\n';
		}
		out.close();
		std::cout << "Wrote timings.csv\n";
	}

	return result;
}
