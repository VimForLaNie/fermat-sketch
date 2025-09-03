#ifndef SKETCH_H
#define SKETCH_H

#include <vector>
#include <deque>
#include <unordered_map>
#include "./row.h"
using namespace std;
class Sketch
{
private:
	int rows_cnt;
	long long p;
	int k;
	int rc;
	std::vector<Rows> rows;
	std::unordered_map<long long, int> flowset;

public:
	// Constructor
	Sketch(int rows_cnt_, int buckets_cnt, long long p_, int k_, int rc_)
		: rows_cnt(rows_cnt_), p(p_), k(k_), rc(rc_)
	{
		rows.reserve(rows_cnt);
		for (int i = 0; i < rows_cnt; i++)
		{
			rows.emplace_back(Rows(buckets_cnt, p, k, rc));
		}
	}

	// Insert a flow
	void insert(long long f)
	{
		for (auto &row : rows)
		{
			row.insert(f);
		}
	}

	// Verify flows
	std::unordered_map<long long, int> verify()
	{
		std::deque<std::pair<int, int>> queue;
		int stop = 0;

		// initialize queue
		for (int i = 0; i < rows_cnt; i++)
		{
			for (int j = 0; j < rows[i].kbuckets.size(); j++)
			{
				const auto &bucket_counts = rows[i].kbuckets[j].get_count();
				bool nonzero = false;
				for (int c : bucket_counts)
				{
					if (c > 0)
					{
						nonzero = true;
						break;
					}
				}
				if (nonzero)
				{
					queue.emplace_back(i, j);
				}
			}
		}

		// process queue
		while (!queue.empty())
		{
			auto [i, j] = queue.front();
			queue.pop_front();
			// cout << "queue size: " << queue.size() << "\n";

			auto counts = rows[i].kbuckets[j].get_count();
			bool all_zero = true;
			for (int c : counts)
			{
				if (c != 0)
				{
					all_zero = false;
					break;
				}
			}
			if (all_zero)
				continue;

			auto k_candidates = rows[i].pure_verification(j);
			if (k_candidates.empty())
			{
				queue.emplace_back(i, j);
				stop++;
				if (stop >= static_cast<int>(queue.size()) + 1)
				{
					break; // cannot decode further
				}
			}
			else
			{
				for (auto &[f, cnt] : k_candidates)
				{
					for (auto &row : rows)
					{
						row.delete_item(f, cnt);
					}
					flowset[f] += cnt;
				}
				stop = 0;
			}
		}

		return flowset;
	}
};

#endif // SKETCH_H
