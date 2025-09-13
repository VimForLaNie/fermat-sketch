// main.cpp
#include <iostream>
#include <random>
#include <unordered_map>
#include <vector>
#include <ctime>
#include <iomanip>
#include "./sketch.h" // your Sketch header
#include "./find_buckets.h"

int main()
{
	// what we vary on x-axis (number of insert events)
	std::vector<int> insert_counts = {20};

	// parameters
	double target_recall = 0.99; // 99%
	int trials = 10;			 // average over trials
	int rows_cnt = 3;
	int k = 2;
	int rc = 4;
	long long p = 4294967291LL;
	cout << "Using prime p=" << p << "\n";
	int flow_id_min = 1;
	int flow_id_max = 1000;
	int min_buckets = 100;
	int max_buckets = 1 << 16; // 65536

	std::vector<int> buckets_needed = find_min_buckets_for_insert_counts(
		insert_counts,
		target_recall,
		trials,
		rows_cnt,
		k,
		rc,
		p,
		flow_id_min,
		flow_id_max,
		min_buckets,
		max_buckets);

	std::cout << "\nSummary (inserts -> required buckets):\n";
	for (size_t i = 0; i < insert_counts.size(); ++i)
	{
		std::cout << insert_counts[i] << " -> " << buckets_needed[i] << "\n";
	}

	return 0;
}

// #include "find_prob.h"
// #include "find_mean_recall.h"

// int main()
// {
// 	int flow_size = 200; // single flow size
// 	std::vector<int> bucket_counts = {125, 250, 500, 1000};

// 	auto means = FindMeanRecalls::find_mean_accuracies_for_buckets(
// 		flow_size, bucket_counts, /*trials=*/500, /*rows=*/3, /*k=*/2, /*rc=*/6, /*p=*/1000000007LL);
// 	for (size_t i = 0; i < bucket_counts.size(); ++i)
// 		std::cout << "b=" << bucket_counts[i] << " mean_accuracy=" << means[i] << "\n";
// 	std::cout << "[";
// 	for (size_t i = 0; i < bucket_counts.size(); ++i)
// 		std::cout << means[i] << " ,";
// 	std::cout << "]\n";
// 	return 0;
// }