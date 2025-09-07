// find_mean_recalls.h
#pragma once

#include <vector>
#include <random>
#include <unordered_map>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <cmath>
#include <chrono>
#include <numeric>
#include <string>
#include "./sketch.h"

namespace FindMeanRecalls
{

	// compute exact-flow accuracy from truth & recovered
	// returns 1.0 if recovered exactly equals truth (same keys and same counts), else 0.0
	static double compute_exact_accuracy_from_maps(const std::unordered_map<long long, int> &truth,
												   const std::unordered_map<long long, int> &recovered)
	{
		// both empty -> perfect
		if (truth.empty() && recovered.empty())
			return 1.0;

		// sizes must match (quick reject for extra/missing keys)
		if (truth.size() != recovered.size())
			return 0.0;

		for (const auto &kv : truth)
		{
			long long fid = kv.first;
			int true_cnt = kv.second;
			auto it = recovered.find(fid);
			if (it == recovered.end())
				return 0.0; // missing key -> not exact
			if (it->second != true_cnt)
				return 0.0; // different count -> not exact
		}

		// all keys present with exact counts
		return 1.0;
	}

	// run trials for a single config: returns vector of trial accuracies (0.0 or 1.0) and per-trial elapsed secs
	static void run_trials_collect_item_recalls(int rows_cnt,
												int buckets_cnt,
												long long p,
												int k,
												int rc,
												int flow_size,
												int trials,
												int flow_id_min,
												int flow_id_max,
												std::mt19937 &rng,
												std::vector<double> &out_trial_accuracies,
												std::vector<double> &out_times)
	{
		out_trial_accuracies.clear();
		out_times.clear();
		out_trial_accuracies.reserve(trials);
		out_times.reserve(trials);

		std::uniform_int_distribution<int> dist_flow(flow_id_min, flow_id_max);

		for (int t = 0; t < trials; ++t)
		{
			Sketch sketch(rows_cnt, buckets_cnt, p, k, rc);
			std::vector<int> events;
			events.reserve(flow_size);

			auto t0 = std::chrono::steady_clock::now();

			for (int i = 0; i < flow_size; ++i)
			{
				int f = dist_flow(rng);
				events.push_back(f);
				sketch.insert(f);
			}

			// build truth
			std::unordered_map<long long, int> truth;
			for (int f : events)
				truth[f]++;

			// decode
			auto recovered = sketch.verify();

			auto t1 = std::chrono::steady_clock::now();
			std::chrono::duration<double> elapsed = t1 - t0;

			double trial_accuracy = compute_exact_accuracy_from_maps(truth, recovered);
			out_trial_accuracies.push_back(trial_accuracy);
			out_times.push_back(elapsed.count());
		}
	}

	// helpers
	static double mean(const std::vector<double> &v)
	{
		if (v.empty())
			return 0.0;
		double s = std::accumulate(v.begin(), v.end(), 0.0);
		return s / static_cast<double>(v.size());
	}
	static double stddev(const std::vector<double> &v, double mu)
	{
		if (v.size() <= 1)
			return 0.0;
		double s = 0.0;
		for (double x : v)
			s += (x - mu) * (x - mu);
		return std::sqrt(s / static_cast<double>(v.size()));
	}

	/*
	 Main function (semantics updated):
	  - flow_size: number of insert events per trial
	  - bucket_counts: vector of bucket sizes to test
	  - trials: trials per bucket
	  - rows_cnt, k, rc, p: sketch params
	  - flow_id_min..flow_id_max: flow id generation range
	  - out_filename: CSV output (Bucket,MeanExactAccuracy,StdExactAccuracy,MeanTimeSec,StdTimeSec)
	  - seed: 0 -> random_device, else fixed seed
	 Returns vector<double> of mean exact accuracies (same order as bucket_counts).
	*/
	static std::vector<double> find_mean_accuracies_for_buckets(
		int flow_size,
		const std::vector<int> &bucket_counts,
		int trials = 500,
		int rows_cnt = 3,
		int k = 2,
		int rc = 4,
		long long p = 1000000007LL,
		int flow_id_min = 1,
		int flow_id_max = 1000,
		const std::string &out_filename = "mean_recalls.csv",
		unsigned int seed = 0)
	{
		std::random_device rd;
		std::mt19937 rng(seed ? seed : rd());

		size_t B = bucket_counts.size();
		std::vector<double> mean_accuracies;
		mean_accuracies.reserve(B);

		// output rows to write later
		struct Row
		{
			int bucket;
			double mean_exact;
			double std_exact;
			double mean_time;
			double std_time;
		};
		std::vector<Row> rows;
		rows.reserve(B);

		std::vector<double> trial_accuracies;
		std::vector<double> times;

		for (size_t bi = 0; bi < B; ++bi)
		{
			int buckets = bucket_counts[bi];

			// progress line (overwrite)
			std::cout << "\rTesting bucket " << (bi + 1) << "/" << B
					  << " (size=" << buckets << ") ..." << std::flush;

			run_trials_collect_item_recalls(rows_cnt, buckets, p, k, rc,
											flow_size, trials, flow_id_min, flow_id_max,
											rng, trial_accuracies, times);

			double mean_exact = mean(trial_accuracies);
			double std_exact = stddev(trial_accuracies, mean_exact);
			double mean_t = mean(times);
			double std_t = stddev(times, mean_t);

			rows.push_back({buckets, mean_exact, std_exact, mean_t, std_t});
			mean_accuracies.push_back(mean_exact);
		}

		std::cout << "\rDone testing " << B << " buckets.                           \n";

		// write CSV
		std::ofstream out(out_filename);
		if (!out)
		{
			std::cerr << "Failed to open " << out_filename << " for writing\n";
			return mean_accuracies;
		}

		out << "Bucket,MeanExactAccuracy,StdExactAccuracy,MeanTimeSec,StdTimeSec\n";
		out << std::fixed << std::setprecision(6);
		for (const auto &r : rows)
		{
			out << r.bucket << "," << r.mean_exact << "," << r.std_exact << "," << r.mean_time << "," << r.std_time << "\n";
		}
		out.close();
		std::cout << "Wrote " << out_filename << "\n";

		return mean_accuracies;
	}

} // namespace FindMeanRecalls
