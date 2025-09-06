// find_buckets.h  (or put into main.cpp)
#pragma once

#include <vector>
#include <random>
#include <unordered_map>
#include <algorithm>
#include <iostream>
#include <numeric>
#include <functional>
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

/*
 find_min_buckets_for_insert_counts
  - insert_counts: vector of total insert events (x-axis)
  - target_recall: e.g. 0.999 (99.9%)
  - trials: number of trials per tested bucket_count (averaged)
  - rows_cnt, k, rc, p: sketch parameters
  - flow_id_range: [flow_id_min, flow_id_max] used to generate flows
  - min_buckets, max_buckets: search limits
  returns vector<int> required_buckets (same length as insert_counts). -1 means not found up to max_buckets.
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

	for (int inserts : insert_counts)
	{
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
				// cout << "Inserts " << inserts << ": testing buckets=" << high << "\n";
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
			// cout << "Inserts " << inserts << ": testing buckets=" << mid << " (range " << left << "-" << right << ")\n";
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
		result.push_back(left);
		std::cout << "Inserts " << inserts << ": required buckets = " << left << " (target recall=" << target_recall << ")\n";
	}

	return result;
}
