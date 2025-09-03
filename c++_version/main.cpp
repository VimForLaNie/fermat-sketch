#include <iostream>
#include <random>
#include "./sketch.h"

int main()
{
	// Parameters
	int rows_cnt = 2;	   // number of rows
	int buckets_cnt = 400; // number of buckets per row
	long long p = 1e9 + 7; // prime modulus
	int k = 2;			   // number of sub-buckets
	int rc = 20;		   // range for g()

	// Create sketch
	Sketch sketch(rows_cnt, buckets_cnt, p, k, rc);

	// Random generator for flows
	std::mt19937 rng(static_cast<unsigned int>(time(nullptr)));
	std::uniform_int_distribution<int> dist_flow(1, 50);

	// Insert flows
	std::cout << "Inserting flows...\n";
	for (int i = 0; i < 20; i++)
	{
		int flow = dist_flow(rng);
		sketch.insert(flow);
		std::cout << "Inserted flow: " << flow << "\n";
	}

	// Verify flows
	std::cout << "\nDecoding flows...\n";
	auto decoded = sketch.verify();

	// Print decoded results
	std::cout << "Decoded flow set:\n";
	for (const auto &[f, cnt] : decoded)
	{
		std::cout << "Flow " << f << " -> Count " << cnt << "\n";
	}

	return 0;
}
