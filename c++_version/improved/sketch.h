#ifndef SKETCH_H
#define SKETCH_H

#include <vector>
#include <deque>
#include <unordered_map>
#include "./row.h"
#include <queue>
#include "./jittatcore.h"

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
	vector<vector<vector<int>>> g_list[10];
	Sketch(int rows_cnt_, int buckets_cnt, long long p_, int k_, int rc_)
		: rows_cnt(rows_cnt_), p(p_), k(k_), rc(rc_)
	{
		// cout << "Using prime p=" << p << "\n";
		// cout << "Sketch init" << endl;
		for (int i = 1; i <= k; i++)
		{
			g_list[i - 1] = MatrixUtils::brute_force_k2_2d(i, rc);
			// cout << "g_list[" << i << "] size: " << g_list[i - 1].size() << "\n";
		}
		rows.reserve(rows_cnt);
		for (int i = 0; i < rows_cnt; i++)
		{
			rows.emplace_back(Rows(buckets_cnt, p, k, rc, i));
		}
	}

	// Insert a flow
	void insert(long long f, int cnt = 1)
	{
		for (auto &row : rows)
		{
			row.insert(f, cnt);
		}
	}

	// Verify flows
	std::unordered_map<long long, int> verify()
	{
		queue<std::pair<int, int>> q;
		int stop = 0;

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
					continue;
				auto k_candidates = rows[i].pure_verification(j, g_list);
				if (!k_candidates.empty())
				{
					for (auto &[f, cnt] : k_candidates)
					{
						for (auto &row : rows)
						{
							row.delete_item(f, cnt);
						}
						flowset[f] += cnt;
					}
				}
			}
		}

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
					q.push({i, j});
				}
			}
		}

		// process queue
		while (!q.empty())
		{
			auto [i, j] = q.front();
			q.pop();
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

			auto k_candidates = rows[i].pure_verification(j, g_list);
			if (k_candidates.empty())
			{
				q.push({i, j});
				stop++;
				if (stop >= static_cast<int>(q.size()) + 1)
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
