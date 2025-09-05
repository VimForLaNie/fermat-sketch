// main.cpp
#include <iostream>
#include <random>
#include <unordered_map>
#include <vector>
#include <ctime>
#include <iomanip>
#include "./sketch.h" // your Sketch header

int main()
{
	// Parameters
	int rows_cnt = 1;			// number of rows
	int buckets_cnt = 200;		// number of buckets per row
	long long p = 1000000007LL; // prime modulus
	int k = 2;					// number of sub-buckets
	int rc = 10;				// range for g()

	// Create sketch
	Sketch sketch(rows_cnt, buckets_cnt, p, k, rc);

	// Random generator for flows
	std::mt19937 rng(static_cast<unsigned int>(std::time(nullptr)));
	std::uniform_int_distribution<int> dist_flow(1, 200);

	// Build flow input (with duplicates allowed)
	const int total_inserts = 200; // number of insert events
	std::vector<int> flow_events;
	flow_events.reserve(total_inserts);
	for (int i = 0; i < total_inserts; ++i)
	{
		int flow = dist_flow(rng);
		flow_events.push_back(flow);
		sketch.insert(flow);
	}

	// Build ground truth counts (distinct flows -> frequency)
	std::unordered_map<long long, int> truth;
	for (int f : flow_events)
		truth[f]++;

	// Run verification / decoding
	std::cout << "Decoding flows...\n";
	std::unordered_map<long long, int> recovered = sketch.verify();

	// Compare recovered vs truth
	int total_flows = static_cast<int>(truth.size()); // distinct victim flows
	int correct = 0;
	int missing_count = 0; // missing or mismatched counted as FN
	int extra_count = 0;   // recovered flows not in truth (FP)
	int mismatched = 0;

	for (const auto &entry : truth)
	{
		long long f = entry.first;
		int true_cnt = entry.second;
		auto it = recovered.find(f);
		if (it == recovered.end())
		{
			missing_count++;
		}
		else
		{
			int rec_cnt = it->second;
			if (rec_cnt == true_cnt)
			{
				correct++;
			}
			else
			{
				mismatched++;
				missing_count++;
			}
		}
	}

	for (const auto &entry : recovered)
	{
		long long f = entry.first;
		if (truth.find(f) == truth.end())
		{
			extra_count++;
		}
	}

	// rates (match Python semantics you used earlier)
	double accuracy = (total_flows > 0) ? static_cast<double>(correct) / total_flows : 0.0;
	double fn_rate = (total_flows > 0) ? static_cast<double>(missing_count) / total_flows : 0.0;
	double fp_rate = 0.0;
	if ((extra_count + correct) > 0)
		fp_rate = static_cast<double>(extra_count) / (extra_count + correct);

	// Print results
	std::cout << std::fixed << std::setprecision(4);
	std::cout << "Ground-truth distinct flows: " << total_flows << "\n";
	std::cout << "Recovered distinct flows : " << recovered.size() << "\n";
	std::cout << "Correctly recovered (exact count match): " << correct << "\n";
	std::cout << "Mismatched count: " << mismatched << "\n";
	std::cout << "Missing (false negatives): " << missing_count << "\n";
	std::cout << "Extra (false positives): " << extra_count << "\n\n";

	std::cout << "Accuracy = " << accuracy * 100.0 << "%\n";
	std::cout << "False negative rate = " << fn_rate * 100.0 << "%\n";
	std::cout << "False positive rate = " << fp_rate * 100.0 << "%\n\n";

	// Optional: print details if small
	if (total_flows <= 50)
	{
		std::cout << "Truth (flow -> count):\n";
		for (auto &t : truth)
			std::cout << "  " << t.first << " -> " << t.second << "\n";
		std::cout << "Recovered (flow -> count):\n";
		for (auto &r : recovered)
			std::cout << "  " << r.first << " -> " << r.second << "\n";
	}

	return 0;
}
