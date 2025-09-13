// Kbucket.h
#ifndef KBUCKET_H
#define KBUCKET_H

#include <vector>
#include "./bucket.h"
using namespace std;
class Kbucket
{
private:
	std::vector<Bucket> buckets;
	int k;

public:
	Kbucket(int k, long long p, int rc, uint32_t hash) : k(k)
	{
		// cout << "Kbucket init" << endl;
		for (int i = 0; i < k; i++)
		{
			buckets.emplace_back(Bucket(p, rc, k, hash + i + 1));
		}
	}

	std::vector<int> insert(int f, int cnt = 1)
	{
		std::vector<int> g;
		g.reserve(buckets.size());
		for (int i = 0; i < buckets.size(); i++)
		{
			g.push_back(buckets[i].insert(f, i, cnt));
		}
		return g;
	}

	void deleteItem(int f, int cnt)
	{
		for (int i = 0; i < buckets.size(); i++)
		{
			buckets[i].deleteItem(f, cnt, i);
		}
	}

	std::vector<int> get_count()
	{
		std::vector<int> counts;
		counts.reserve(buckets.size());
		for (auto &bucket : buckets)
		{
			counts.push_back(bucket.get_count());
		}
		return counts;
	}
	const std::vector<Bucket> &getBuckets() const
	{
		return buckets;
	}
};

#endif // KBUCKET_H
