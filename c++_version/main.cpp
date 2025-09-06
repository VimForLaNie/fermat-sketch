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
	std::vector<int> insert_counts = {40, 80, 120, 200};

	// parameters
	double target_recall = 0.99; // 99%
	int trials = 500;			 // average over trials
	int rows_cnt = 1;
	int k = 2;
	int rc = 4;
	long long p = 1000000007LL;
	int flow_id_min = 1;
	int flow_id_max = 5000;
	int min_buckets = 64;
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