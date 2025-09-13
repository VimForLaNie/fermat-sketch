#ifndef BUCKET_H
#define BUCKET_H

#include <vector>
#include <random>
#include <ctime>
#include <cstdint>
#include <stdexcept>
#include <mutex>
using namespace std;
// small prime table used by g(); make sure rc * k <= PRIME_COUNT
static const int PRIME_LIST[] = {
	2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53,
	59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
	127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181,
	191, 193, 197, 199};
static const int PRIME_COUNT = sizeof(PRIME_LIST) / sizeof(PRIME_LIST[0]);

// simple thread-safe single RNG (seeded once)
inline std::mt19937 &global_rng()
{
	static std::mt19937 rng((std::random_device()()));
	return rng;
}

class Bucket
{
public:
	// public read-only accessors (prefer getters rather than public fields)
	int getCount() const { return count; }
	long long getId() const { return id; }
	long long count; // weighted count (sum of g contributions)
	long long id;	 // sum of g(f)*f

private:
	long long p; // modulus (prime)
	int rc;		 // number of possible column choices for g
	int _a;
	int _b;
	int k; // number of sub-buckets in a Kbucket
	uint32_t hash;

	// modular exponentiation (a^b % mod) - works for mod up to 2^31
	static long long
	mod_pow(long long base, long long exp, long long mod)
	{
		long long res = 1 % mod;
		base %= mod;
		while (exp > 0)
		{
			if (exp & 1LL)
				res = (res * base) % mod;
			base = (base * base) % mod;
			exp >>= 1LL;
		}
		return res;
	}

public:
	// Constructor
	// Note: ensure externally that k * rc <= PRIME_COUNT
	Bucket(long long p_, int rc_, int k_, uint32_t hash)
		: count(0), id(0), p(p_), rc(rc_), _a(1), _b(0), k(k_), hash(hash)
	{
		// cout << "Bucket init" << endl;
		if (rc_ <= 0 || k_ <= 0)
			throw std::invalid_argument("rc and k must be > 0");
		if (k_ * rc_ > PRIME_COUNT)
			throw std::invalid_argument("k * rc exceeds prime table size");

		// use single global RNG to avoid identical seeds
		std::uniform_int_distribution<int> distA(1, std::max((long long)1, p - 1));
		std::uniform_int_distribution<int> distB(0, std::max(0ll, p - 1));
		_a = distA(global_rng());
		_b = distB(global_rng());
	}

	// g(f, row) returns an integer weight from the prime table.
	// row must be in [0, k-1].
	int g(int f, int row) const
	{
		if (row < 0 || row >= k)
			throw std::out_of_range("row index out of range in Bucket::g");
		// compute column index 0..rc-1 from (a*f + b) mod p
		uint32_t val = MurmurHash3_x86_32(&f, sizeof(f), hash);
		int col = static_cast<int>(val % rc);
		int idx = col + row * rc;
		// idx guaranteed < PRIME_COUNT by constructor check
		return PRIME_LIST[idx];
	}

	// Insert increments count and id; returns gval used
	int insert(int flow_id, int row, long long cnt = 1)
	{
		int gval = g(flow_id, row);
		count += ((long long)gval * cnt) % p;
		count %= p;
		id += (((static_cast<long long>(gval) * static_cast<long long>(flow_id)) % p) * cnt) % p;
		return gval;
	}

	// deleteItem subtracts occurrences (cnt times)
	void deleteItem(int flow_id, long long cnt, int row)
	{
		int gval = g(flow_id, row);
		long long dec = static_cast<long long>(cnt) * static_cast<long long>(gval) % p;
		if (dec < 0)
			return; // defensive
		if (dec >= count)
		{
			count -= dec;
			count += p;
			count %= p;
		}
		else
		{
			count -= static_cast<int>(dec);
		}
		// update id modulo p; keep id in [0,p-1]
		long long delta = (static_cast<long long>(gval) * static_cast<long long>(flow_id) * cnt) % p;
		id = (id - delta) % p;
		if (id < 0)
			id += p;
	}

	// Return (sum_id, count). If count == 0 returns (0,0).
	// sum_id = id * inv(count) mod p  (assuming p is prime and count != 0)
	std::pair<long long, long long> get_sumid_and_count() const
	{
		if (count == 0)
			return {0LL, 0};
		// compute modular inverse of count mod p using Fermat (p must be prime)
		long long inv = mod_pow(static_cast<long long>(count), static_cast<long long>(p) - 2LL, p);
		long long sum_id = ((id % p + p) % p) * inv % p;
		return {sum_id, count};
	}

	// convenience: direct access to count (kept for compatibility)
	long long get_count() const { return count; }

}; // end class Bucket

#endif // BUCKET_H
