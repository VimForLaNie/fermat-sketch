// Bucket.h
#ifndef BUCKET_H
#define BUCKET_H

#include <vector>
#include <random>
#include <ctime>

// List of primes (same as Python version)
static const int prime_list[] = {
	2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
	73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
	157, 163, 167, 173, 179, 181, 191, 193, 197, 199};

class Bucket
{
public:
	int count;
	long long id;

private:
	int p;
	int rc;
	int _a;
	int _b;
	int k;

	// modular exponentiation (like Python pow(a,b,p))
	long long mod_pow(long long base, long long exp, int mod)
	{
		long long result = 1;
		base %= mod;
		while (exp > 0)
		{
			if (exp & 1)
				result = (result * base) % mod;
			base = (base * base) % mod;
			exp >>= 1;
		}
		return result;
	}

public:
	Bucket(int p, int rc, int k) : p(p), rc(rc), k(k)
	{
		count = 0;
		id = 0;
		// Random generator for _a, _b
		std::mt19937 rng(static_cast<unsigned int>(std::time(nullptr)));
		std::uniform_int_distribution<int> dist_a(1, p - 1);
		std::uniform_int_distribution<int> dist_b(0, p - 1);
		_a = dist_a(rng);
		_b = dist_b(rng);
	}

	int g(int f, int i) const
	{
		// Build arr like Python version
		std::vector<std::vector<int>> arr(k, std::vector<int>(rc));
		for (int j = 0; j < k; j++)
		{
			for (int x = 0; x < rc; x++)
			{
				arr[j][x] = prime_list[i + j * rc];
			}
		}
		return arr[i][((_a * f + _b) % p) % rc];
	}

	int insert(int flow_id, int i)
	{
		int gval = g(flow_id, i);
		count += gval;
		id += static_cast<long long>(gval) * flow_id;
		return gval;
	}

	void deleteItem(int flow_id, int cnt, int i)
	{
		int gval = g(flow_id, i);
		if (count < cnt * gval)
		{
			count = 0;
		}
		else
		{
			count -= cnt * gval;
		}
		id = (id - static_cast<long long>(gval) * flow_id * cnt) % p;
		if (id < 0)
			id += p; // ensure positive modulo
	}

	std::pair<long long, int> get_sumid_and_count()
	{
		long long sum_id = (id * mod_pow(count, p - 2, p)) % p;
		return {sum_id, count};
	}

	int get_count() const
	{
		return count;
	}
};

#endif // BUCKET_H
