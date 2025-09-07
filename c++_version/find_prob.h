#pragma once

#include <vector>
#include <random>
#include <unordered_map>
#include <iostream>
#include <fstream>
#include <iomanip>
#include "./sketch.h"

// ---- Compute item-level recall for one run ----
static double compute_item_recall_single_run(Sketch &sketch,
											 const std::vector<int> &flow_events)
{
	std::unordered_map<long long, int> truth;
	for (int f : flow_events)
		truth[f]++;

	long long total_items = 0, fn_total = 0;
	for (const auto &kv : truth)
		total_items += kv.second;

	auto recovered = sketch.verify();

	for (const auto &kv : truth)
	{
		long long fid = kv.first;
		int true_cnt = kv.second;
		int rec_cnt = 0;
		auto it = recovered.find(fid);
		if (it != recovered.end())
			rec_cnt = it->second;

		if (rec_cnt < true_cnt)
			fn_total += (true_cnt - rec_cnt);
	}

	if (total_items == 0)
		return 1.0;

	return static_cast<double>(total_items - fn_total) / static_cast<double>(total_items);
}

// ---- Run trials and compute probability ----
static double probability_for_config(int rows_cnt,
									 int buckets_cnt,
									 long long p,
									 int k,
									 int rc,
									 int inserts_per_trial,
									 int trials,
									 int flow_id_min,
									 int flow_id_max,
									 double target_recall,
									 std::mt19937 &rng)
{
	std::uniform_int_distribution<int> dist_flow(flow_id_min, flow_id_max);
	int success = 0;

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
		if (recall >= target_recall)
			success++;
	}

	return static_cast<double>(success) / static_cast<double>(trials);
}

/*
 find_probabilities_for_buckets_simple
  - flow_size: number of inserts per trial
  - bucket_counts: array of candidate bucket sizes
  - returns vector<double> of probabilities (same order as bucket_counts)
  - also writes results into "probabilities.csv"
*/
static std::vector<double> find_probabilities_for_buckets_simple(
	int flow_size,
	const std::vector<int> &bucket_counts,
	double target_recall = 0.99,
	int trials = 20,
	int rows_cnt = 1,
	int k = 2,
	int rc = 10,
	long long p = 1000000007LL,
	int flow_id_min = 1,
	int flow_id_max = 1000)
{
	std::random_device rd;
	std::mt19937 rng(rd());

	std::vector<double> result(bucket_counts.size(), 0.0);

	for (size_t bi = 0; bi < bucket_counts.size(); ++bi)
	{
		int buckets = bucket_counts[bi];
		double prob = probability_for_config(rows_cnt, buckets, p, k, rc,
											 flow_size, trials,
											 flow_id_min, flow_id_max,
											 target_recall, rng);
		result[bi] = prob;
		std::cout << "Buckets=" << buckets
				  << " → Prob=" << prob << "\n";
	}

	// Write CSV file
	std::ofstream out("probabilities.csv");
	if (out)
	{
		out << "Buckets,Probability\n";
		for (size_t bi = 0; bi < bucket_counts.size(); ++bi)
		{
			out << bucket_counts[bi] << ","
				<< std::fixed << std::setprecision(6) << result[bi] << "\n";
		}
		out.close();
		std::cout << "Wrote probabilities.csv\n";
	}
	else
	{
		std::cerr << "Failed to open probabilities.csv for writing\n";
	}

	return result;
}
