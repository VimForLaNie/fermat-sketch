// find_probabilities.h
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

/*
  find_probabilities_for_buckets_simple

  - flow_size: number of insert events per trial (single flow size)
  - bucket_counts: array of bucket counts to test
  - target_recall: threshold (e.g. 0.99)
  - trials: number of independent trials per bucket_count
  - rows_cnt, k, rc, p: sketch parameters
  - flow_id_min..flow_id_max: ID range for random flows
  - out_filename: CSV output file (default "probabilities.csv")
  - seed: optional seed (0 => random_device)
  - returns vector of probabilities (same order as bucket_counts)

  CSV columns: Bucket,Probability,MeanTimeSec,StdTimeSec
*/

namespace FindProb
{

	static double compute_item_recall_single_runs(Sketch &sketch,
												  const std::vector<int> &flow_events)
	{
		std::unordered_map<long long, int> truth;
		for (int f : flow_events)
			truth[f]++;

		long long total_items = 0;
		long long fn_total = 0;
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

	// run trials for one config, returning probability and per-trial times
	static std::pair<double, std::vector<double>> run_trials_for_bucket(
		int rows_cnt,
		int buckets_cnt,
		long long p,
		int k,
		int rc,
		int flow_size,
		int trials,
		int flow_id_min,
		int flow_id_max,
		double target_recall,
		std::mt19937 &rng)
	{
		std::uniform_int_distribution<int> dist_flow(flow_id_min, flow_id_max);
		int success = 0;
		std::vector<double> times;
		times.reserve(trials);

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

			double recall = compute_item_recall_single_runs(sketch, events);

			auto t1 = std::chrono::steady_clock::now();
			std::chrono::duration<double> elapsed = t1 - t0;
			times.push_back(elapsed.count());

			if (recall >= target_recall)
				success++;
		}

		double prob = (trials > 0) ? static_cast<double>(success) / static_cast<double>(trials) : 0.0;
		return {prob, times};
	}

	static double mean_of_vector(const std::vector<double> &v)
	{
		if (v.empty())
			return 0.0;
		double s = std::accumulate(v.begin(), v.end(), 0.0);
		return s / static_cast<double>(v.size());
	}

	static double std_of_vector(const std::vector<double> &v, double mean)
	{
		if (v.size() <= 1)
			return 0.0;
		double s = 0.0;
		for (double x : v)
			s += (x - mean) * (x - mean);
		return std::sqrt(s / static_cast<double>(v.size()));
	}

	/*
	 Main function you call from your program.
	*/
	static std::vector<double> find_probabilities_for_buckets_simple(
		int flow_size,
		const std::vector<int> &bucket_counts,
		double target_recall = 0.99,
		int trials = 50,
		int rows_cnt = 1,
		int k = 2,
		int rc = 10,
		long long p = 1000000007LL,
		int flow_id_min = 1,
		int flow_id_max = 1000,
		const std::string &out_filename = "probabilities.csv",
		unsigned int seed = 0)
	{
		std::random_device rd;
		std::mt19937 rng(seed ? seed : rd());

		size_t B = bucket_counts.size();
		std::vector<double> probabilities(B, 0.0);

		// CSV output prepare (we fill after computing)
		struct RowResult
		{
			int bucket;
			double prob;
			double mean_time;
			double std_time;
		};
		std::vector<RowResult> rows;
		rows.reserve(B);

		for (size_t bi = 0; bi < B; ++bi)
		{
			int buckets = bucket_counts[bi];

			// progress print (overwrites same line)
			std::cout << "\rTesting bucket " << (bi + 1) << "/" << B
					  << " (size=" << buckets << ") ..." << std::flush;

			auto [prob, times] = run_trials_for_bucket(rows_cnt, buckets, p, k, rc,
													   flow_size, trials,
													   flow_id_min, flow_id_max,
													   target_recall, rng);

			double mean_t = mean_of_vector(times);
			double std_t = std_of_vector(times, mean_t);

			rows.push_back({buckets, prob, mean_t, std_t});
			probabilities[bi] = prob;
		}

		// finish progress line
		std::cout << "\rDone testing " << B << " buckets.                         \n";

		// write CSV
		std::ofstream out(out_filename);
		if (!out)
		{
			std::cerr << "Failed to open " << out_filename << " for writing\n";
			return probabilities;
		}
		out << "Bucket,Probability,MeanTimeSec,StdTimeSec\n";
		out << std::fixed << std::setprecision(6);
		for (const auto &r : rows)
		{
			out << r.bucket << "," << r.prob << "," << r.mean_time << "," << r.std_time << "\n";
		}
		out.close();
		std::cout << "Wrote " << out_filename << "\n";

		return probabilities;
	}

} // namespace FindProb
