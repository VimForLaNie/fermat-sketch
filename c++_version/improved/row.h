#ifndef ROWS_H
#define ROWS_H

#include <vector>
#include <random>
#include <utility>
#include <cmath>
#include <Eigen/Dense>
#include "util/murmur3.h"

#include "./kbucket.h"	  // must provide Kbucket and getBuckets()
#include "./jittatcore.h" // must provide MatrixUtils::brute_force_k2_2d(...)

class Rows
{
private:
	long long p;
	int m;
	int k;
	int rc;
	int index;
	uint32_t hash; // seed for Murmur

	// Helper: convert vector<vector<int>> (matrix) -> Eigen::MatrixXi
	static inline Eigen::MatrixXi
	vectorToEigen(const std::vector<std::vector<int>> &mat, int rows, int cols)
	{
		Eigen::MatrixXi M(rows, cols);
		for (int i = 0; i < rows; ++i)
			for (int j = 0; j < cols; ++j)
				M(i, j) = mat[i][j];
		return M;
	}

	// round if every entry is within tol of an integer
	static inline bool roundIfClose(const Eigen::MatrixXd &M, Eigen::MatrixXi &out, double atol = 1e-8, double rtol = 1e-8)
	{
		out.resize(M.rows(), M.cols());
		for (int i = 0; i < M.rows(); ++i)
		{
			for (int j = 0; j < M.cols(); ++j)
			{
				double v = M(i, j);
				long long r = std::llround(v);
				double tol = atol + rtol * std::max(1.0, std::abs(v));
				if (std::abs(v - static_cast<double>(r)) > tol)
					return false;
				// Note: ensure r fits into int if you cast below
				out(i, j) = static_cast<int>(r);
			}
		}
		return true;
	}

	static inline bool equalInt(const Eigen::MatrixXi &A, const Eigen::MatrixXi &B)
	{
		if (A.rows() != B.rows() || A.cols() != B.cols())
			return false;
		for (int i = 0; i < A.rows(); ++i)
			for (int j = 0; j < A.cols(); ++j)
				if (A(i, j) != B(i, j))
					return false;
		return true;
	}

public:
	// make flow id type consistent across class
	using flow_t = uint32_t;

	std::vector<Kbucket> kbuckets;

	Rows(int m_, long long p_, int k_, int rc_, int index_, int seed = 42)
		: kbuckets(), p(p_), m(m_), k(k_), rc(rc_), index(index_)
	{
		// cout << "Rows init" << endl;
		kbuckets.reserve(static_cast<size_t>(m_));
		hash = static_cast<uint32_t>(seed + (10 * index) + 1u);
		for (int i = 0; i < m_; ++i)
		{
			kbuckets.emplace_back(Kbucket(k_, static_cast<long long>(p_), rc_, hash));
		}

		std::random_device rd;
		std::mt19937_64 gen(rd());
	}

	// Insert an element (returns the g-values from the chosen Kbucket)
	// NOTE: flow_t is the canonical flow id type used for hashing and indexing
	std::vector<int> insert(flow_t f, int cnt = 1)
	{
		// hash exactly the same bytes everywhere: flow_t and sizeof(flow_t)
		uint32_t pos = MurmurHash3_x86_32(&f, sizeof(f), hash) % static_cast<uint32_t>(m);
		// Kbucket::insert expects an int in your original code; cast explicitly
		return kbuckets[pos].insert(static_cast<int>(f), cnt);
	}

	// Pure verification - tries sizes kk=k..1 (like python)
	// std::vector<std::pair<int, int>> pure_verification(int i, vector<vector<vector<int>>> g_list[]) const
	// {
	// 	std::vector<std::pair<int, int>> answer;

	// 	const std::vector<Bucket> &buckets = kbuckets.at(i).getBuckets();

	// 	for (int kk = k; kk >= 1; --kk)
	// 	{
	// 		Eigen::MatrixXi a_mat(kk, 1);
	// 		Eigen::MatrixXi id_mat(kk, 1);

	// 		for (int idx = 0; idx < kk; ++idx)
	// 		{
	// 			a_mat(idx, 0) = static_cast<int>(buckets[idx].count);
	// 			id_mat(idx, 0) = static_cast<int>(buckets[idx].id);
	// 		}

	// 		for (const auto &g_mat_vec : g_list[kk - 1])
	// 		{
	// 			Eigen::MatrixXi g_int = vectorToEigen(g_mat_vec, kk, kk);
	// 			Eigen::MatrixXd g_d = g_int.cast<double>();

	// 			Eigen::FullPivLU<Eigen::MatrixXd> fu_g(g_d);
	// 			if (fu_g.rank() < kk || !fu_g.isInvertible())
	// 				continue;

	// 			Eigen::MatrixXd c_d = fu_g.solve(a_mat.cast<double>());
	// 			// Eigen::MatrixXd c_d = matmul_mod(fu_g, a_mat, p);

	// 			Eigen::MatrixXi c_int;
	// 			if (!roundIfClose(c_d, c_int))
	// 				continue;

	// 			bool any_negative = false;
	// 			for (int r = 0; r < c_int.rows(); ++r)
	// 			{
	// 				if (c_int(r, 0) < 0)
	// 				{
	// 					any_negative = true;
	// 					break;
	// 				}
	// 			}
	// 			if (any_negative)
	// 				continue;

	// 			Eigen::MatrixXi a_check = g_int * c_int;
	// 			if (!equalInt(a_check, a_mat))
	// 				continue;

	// 			Eigen::MatrixXd c_diag = c_int.cast<double>().asDiagonal();
	// 			Eigen::MatrixXd gc_d = g_d * c_diag;

	// 			Eigen::FullPivLU<Eigen::MatrixXd> fu_gc(gc_d);
	// 			if (fu_gc.rank() < kk || !fu_gc.isInvertible())
	// 				continue;

	// 			Eigen::MatrixXd f_d = fu_gc.solve(id_mat.cast<double>());

	// 			Eigen::MatrixXi f_int;
	// 			if (!roundIfClose(f_d, f_int))
	// 				continue;

	// 			// verify hash constraint: each recovered flow must hash to bucket i
	// 			bool ok = true;
	// 			for (int idx = 0; idx < f_int.rows(); ++idx)
	// 			{
	// 				// Use canonical flow type for hashing
	// 				flow_t flow_candidate = static_cast<flow_t>(f_int(idx, 0));
	// 				uint32_t h = MurmurHash3_x86_32(&flow_candidate, sizeof(flow_candidate), hash) % static_cast<uint32_t>(m);
	// 				if (h != static_cast<uint32_t>(i))
	// 				{
	// 					ok = false;
	// 					break;
	// 				}
	// 			}
	// 			if (!ok)
	// 				continue;

	// 			// verify g-consistency
	// 			for (int row = 0; row < kk && ok; ++row)
	// 			{
	// 				for (int col = 0; col < kk; ++col)
	// 				{
	// 					int flow_candidate = f_int(col, 0);
	// 					if (buckets[row].g(flow_candidate, row) != g_int(row, col))
	// 					{
	// 						ok = false;
	// 						break;
	// 					}
	// 				}
	// 			}
	// 			if (!ok)
	// 				continue;

	// 			for (int j = 0; j < kk; ++j)
	// 			{
	// 				answer.emplace_back(f_int(j, 0), c_int(j, 0));
	// 			}
	// 			return answer;
	// 		} // g_list
	// 	} // kk
	// 	return std::vector<std::pair<int, int>>();
	// }
	std::vector<std::pair<int, int>> pure_verification(int i, std::vector<std::vector<std::vector<int>>> g_list[]) const
	{
		std::vector<std::pair<int, int>> answer;

		// basic bounds checks
		if (i < 0 || static_cast<size_t>(i) >= kbuckets.size())
			return answer;
		const std::vector<Bucket> &buckets = kbuckets.at(i).getBuckets();
		long long pmod = p;
		for (int kk = k; kk >= 1; --kk)
		{
			// ensure we have enough buckets to build a_mat/id_mat
			if (static_cast<size_t>(kk) > buckets.size())
				continue;

			std::vector<int> a_vec(kk);
			std::vector<int> id_vec(kk);
			for (int idx = 0; idx < kk; ++idx)
			{
				a_vec[idx] = static_cast<int>(buckets[idx].count);
				id_vec[idx] = static_cast<int>(buckets[idx].id);
				if (pmod != -1)
				{
					a_vec[idx] = (a_vec[idx] % pmod + pmod) % pmod;
					id_vec[idx] = (id_vec[idx] % pmod + pmod) % pmod;
				}
			}

			// ensure g_list is present for this kk
			// NOTE: g_list is a C-array / pointer; caller must ensure it has at least k entries.
			// Defensive: if g_list[kk-1] is empty, continue.
			if (g_list[kk - 1].empty())
				continue;

			// iterate candidate g matrices for this kk
			for (const auto &g_mat_vec : g_list[kk - 1])
			{

				// Attempt modular (or integer) inverse of g
				std::vector<std::vector<int>> g = g_mat_vec; // copy
				// cout << "Finding rank and inverse for kk=" << kk << endl;
				int rank = MatrixUtils::find_rank(g, pmod);
				// cout << "rank: " << rank << endl;
				if (rank < kk)
					continue; // not full rank -> skip
				// cout << "here" << endl;
				// cout << "rank: " << rank << endl;
				try
				{
					// inverse_matrix throws on singular / no modular inverse
					std::vector<std::vector<int>> g_inv = MatrixUtils::inverse_matrix(g, pmod);
					if (g_inv.empty())
						continue; // no inverse -> skip

					// c = g_inv * a_vec  (respecting modulus)
					std::vector<int> c_vec = MatrixUtils::mat_vec_mul(g_inv, a_vec, pmod);

					bool any_negative = false;
					if (pmod == -1)
					{
						for (int val : c_vec)
							if (val < 0)
							{
								any_negative = true;
								break;
							}
					}
					if (any_negative)
						continue;

					// verify g *c == a
					std::vector<int>
						a_check = MatrixUtils::mat_vec_mul(g, c_vec, pmod);
					bool equal = true;
					for (int r = 0; r < kk; ++r)
					{
						int av = a_vec[r];
						int ac = a_check[r];
						if (pmod != -1)
						{
							av = (av % pmod + pmod) % pmod;
							ac = (ac % pmod + pmod) % pmod;
						}
						if (av != ac)
						{
							equal = false;
							break;
						}
					}
					if (!equal)
						continue;
					for (auto &val : c_vec)
					{
						cout << val << " ";
					}
					cout << endl;

					// build gc = g * diag(c) : column j of g multiplied by c[j]
					std::vector<std::vector<int>> gc(kk, std::vector<int>(kk, 0));
					for (int r = 0; r < kk; ++r)
					{
						for (int col = 0; col < kk; ++col)
						{
							long long val = 1LL * g[r][col] * c_vec[col];
							if (pmod != -1)
							{
								val %= pmod;
								if (val < 0)
									val += pmod;
							}
							gc[r][col] = static_cast<int>(val);
						}
					}
					int rank_gc = MatrixUtils::find_rank(gc, pmod);
					if (rank_gc < kk)
						continue; // not full rank -> skip

					// try inverse of gc
					std::vector<std::vector<int>> gc_inv;
					try
					{
						gc_inv = MatrixUtils::inverse_matrix(gc, pmod);
						if (gc_inv.empty())
							continue; // no inverse -> skip
					}
					catch (...)
					{
						// not invertible -> skip
						continue;
					}

					// f = gc_inv * id_vec
					std::vector<int> f_vec = MatrixUtils::mat_vec_mul(gc_inv, id_vec, pmod);

					// f_vec must be valid flow ids (non-negative and fit flow_t)
					bool ok = true;
					for (int idx = 0; idx < kk; ++idx)
					{
						long long fv = f_vec[idx];
						if (pmod != -1)
						{
							// f is modulo p; convert to canonical representative in [0,p-1]
							fv = (fv % pmod + pmod) % pmod;
						}
						if (fv < 0 || fv > static_cast<long long>(std::numeric_limits<int>::max()))
						{
							ok = false;
							break;
						}
					}
					if (!ok)
						continue;

					// verify hash constraint: each recovered flow must hash to bucket i
					for (int idx = 0; idx < kk; ++idx)
					{
						int flow_candidate = f_vec[idx];
						flow_t fc = static_cast<flow_t>(flow_candidate);
						uint32_t h = MurmurHash3_x86_32(&fc, sizeof(fc), hash) % static_cast<uint32_t>(m);
						if (h != static_cast<uint32_t>(i))
						{
							ok = false;
							break;
						}
					}
					if (!ok)
						continue;

					// verify g-consistency: buckets[row].g(flow_candidate, row) == g[row][col]
					for (int row = 0; row < kk && ok; ++row)
					{
						for (int col = 0; col < kk; ++col)
						{
							int flow_candidate = f_vec[col];
							if (buckets[row].g(flow_candidate, row) != g[row][col])
							{
								ok = false;
								break;
							}
						}
					}
					if (!ok)
						continue;

					// success: collect (flow, count) pairs
					for (int j = 0; j < kk; ++j)
					{
						answer.emplace_back(f_vec[j], c_vec[j]);
					}
					return answer;
				}
				catch (const std::exception &e)
				{
					// g not invertible (or modular inverse missing) -> skip candidate
					continue;
				}
			} // end g_list[kk-1] loop
		} // end kk
		return std::vector<std::pair<int, int>>();
	}

	// Delete (remove) flow occurrences
	void delete_item(flow_t f, int cnt)
	{
		uint32_t pos = MurmurHash3_x86_32(&f, sizeof(f), hash) % static_cast<uint32_t>(m);
		kbuckets.at(pos).deleteItem(static_cast<int>(f), cnt);
	}
};

#endif // ROWS_H
