// find_buckets.h  (or put into main.cpp)
#pragma once

#include <vector>
#include <random>
#include <unordered_map>
#include <algorithm>
#include <iostream>
#include <numeric>
#include <functional>
#include <chrono>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <cmath>
#include "./sketch.h"

// Compute item-level recall for one run (same logic you used earlier)
static double compute_item_recall_single_run(Sketch &sketch,
											 const std::vector<int> &flow_events)
{
	// build truth
	std::unordered_map<long long, int> truth;
	for (int f : flow_events)
		truth[f]++;

	long long total_items = 0;
	long long fn_total = 0; // missed items
	long long fp_total = 0; // extra items
	long long recovered_items = 0;

	for (const auto &kv : truth)
		total_items += kv.second;

	auto recovered = sketch.verify();

	// compute fn and partial fp for matched flows
	for (const auto &kv : truth)
	{
		long long fid = kv.first;
		int true_cnt = kv.second;
		auto it = recovered.find(fid);
		int rec_cnt = 0;
		if (it != recovered.end())
		{
			rec_cnt = it->second;
			recovered_items += rec_cnt;
		}
		if (rec_cnt < true_cnt)
			fn_total += (true_cnt - rec_cnt);
		else if (rec_cnt > true_cnt)
			fp_total += (rec_cnt - true_cnt);
	}
	// recovered flows not in truth -> all their items are false positives
	for (const auto &kv : recovered)
	{
		if (truth.find(kv.first) == truth.end())
		{
			fp_total += kv.second;
			recovered_items += kv.second;
		}
	}

	if (total_items == 0)
		return 1.0;
	double recall = static_cast<double>(total_items - fn_total) / static_cast<double>(total_items);
	return recall;
}

// Run multiple trials and return mean item recall
static double mean_recall_for_config(int rows_cnt,
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
	double sum_recall = 0.0;
	for (int t = 0; t < trials; ++t)
	{
		Sketch sketch(rows_cnt, buckets_cnt, p, k, rc);
		std::vector<int> events;
		events.reserve(inserts_per_trial);
		for (int i = 0; i < inserts_per_trial; ++i)
		{
			int f = dist_flow(rng);
			events.push_back(f);
			sketch.insert(f);
		}
		double recall = compute_item_recall_single_run(sketch, events);
		sum_recall += recall;
	}
	return sum_recall / static_cast<double>(trials);
}

// Measure per-trial wallclock times for a given config (returns vector of seconds, length == trials)
static std::vector<double> measure_trial_times(int rows_cnt,
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
	std::vector<double> times;
	times.reserve(trials);

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

		// run decode/verify
		auto recovered = sketch.verify();

		auto t1 = std::chrono::high_resolution_clock::now();
		std::chrono::duration<double> elapsed = t1 - t0;
		times.push_back(elapsed.count());
	}

	return times;
}

/*
 find_min_buckets_for_insert_counts
  - insert_counts: vector of total insert events (x-axis)
  - target_recall: e.g. 0.999 (99.9%)
  - trials: number of trials per tested bucket_count (averaged)
  - rows_cnt, k, rc, p: sketch parameters
  - flow_id_range: [flow_id_min, flow_id_max] used to generate flows
  - min_buckets, max_buckets: search limits
  returns vector<int> required_buckets (same length as insert_counts). -1 means not found up to max_buckets.
  Additionally writes a CSV file "timings.csv" containing per-trial runtimes (seconds).
*/
static std::vector<int> find_min_buckets_for_insert_counts(
	const std::vector<int> &insert_counts,
	double target_recall = 0.999,
	int trials = 5,
	int rows_cnt = 1,
	int k = 2,
	int rc = 10,
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

	// prepare times matrix: rows = trials, cols = insert_counts.size()
	// initialize with NaN for missing entries
	size_t C = insert_counts.size();
	std::vector<std::vector<double>> times_matrix(static_cast<size_t>(trials), std::vector<double>(C, std::numeric_limits<double>::quiet_NaN()));

	for (size_t ci = 0; ci < insert_counts.size(); ++ci)
	{
		int inserts = insert_counts[ci];

		// exponential search for an upper bound
		int low = min_buckets;
		int high = low;
		int found_bucket = -1;

		// check starting point
		double mean_rec = mean_recall_for_config(rows_cnt, high, p, k, rc, inserts, trials, flow_id_min, flow_id_max, rng);
		if (mean_rec >= target_recall)
		{
			found_bucket = high;
		}
		else
		{
			// exponential grow
			while (high <= max_buckets)
			{
				high = high * 2;
				if (high > max_buckets)
				{
					high = max_buckets;
				}
				mean_rec = mean_recall_for_config(rows_cnt, high, p, k, rc, inserts, trials, flow_id_min, flow_id_max, rng);
				if (mean_rec >= target_recall)
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
			// not found up to max_buckets
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
			double recall_mid = mean_recall_for_config(rows_cnt, mid, p, k, rc, inserts, trials, flow_id_min, flow_id_max, rng);
			if (recall_mid >= target_recall)
			{
				right = mid;
			}
			else
			{
				left = mid + 1;
			}
		}

		// left is the minimal bucket count found by search
		result.push_back(left);
		std::cout << "Inserts " << inserts << ": required buckets = " << left << " (target recall=" << target_recall << ")\n";

		// measure per-trial times for this bucket count and store into times_matrix column
		std::vector<double> measured = measure_trial_times(rows_cnt, left, p, k, rc, inserts, trials, flow_id_min, flow_id_max, rng);

		// fill into column ci
		for (int t = 0; t < trials; ++t)
		{
			times_matrix[static_cast<size_t>(t)][ci] = measured[static_cast<size_t>(t)];
		}
	}

	// Write CSV file "timings.csv" with header showing insert counts
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
					out << ""; // leave empty for not-found
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
