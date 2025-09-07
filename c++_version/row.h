#ifndef ROWS_H
#define ROWS_H

#include <vector>
#include <random>
#include <utility>
#include <cmath>
#include <Eigen/Dense>

#include "./kbucket.h"	  // must provide Kbucket and getBuckets()
#include "./jittatcore.h" // must provide MatrixUtils::brute_force_k2_2d(...)
using namespace std;
class Rows
{
private:
	long long p;
	int m;
	long long a, b;
	int k;
	int rc;

	// Hash function (equivalent to Python version)
	inline int hash(long long f) const
	{
		return static_cast<int>(((a * f + b) % p + p) % p % m);
	}

	// Helper: convert vector<vector<int>> (matrix) -> Eigen::MatrixXi
	static inline Eigen::MatrixXi vectorToEigen(const std::vector<std::vector<int>> &mat, int rows, int cols)
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
				out(i, j) = static_cast<int>(r);
			}
		}
		return true;
	}

	// exact integer equality check
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
	// Constructor
	std::vector<Kbucket> kbuckets;
	Rows(int m_, long long p_, int k_, int rc_)
		: kbuckets(), p(p_), m(m_), a(0), b(0), k(k_), rc(rc_)
	{
		kbuckets.reserve(static_cast<size_t>(m_));
		for (int i = 0; i < m_; ++i)
		{
			kbuckets.emplace_back(Kbucket(k_, static_cast<int>(p_), rc_));
		}

		std::random_device rd;
		std::mt19937_64 gen(rd());
		std::uniform_int_distribution<long long> dist_a(1, p - 1);
		std::uniform_int_distribution<long long> dist_b(0, p - 1);

		a = dist_a(gen);
		b = dist_b(gen);
	}

	// Insert an element (returns the g-values from the chosen Kbucket)
	std::vector<int> insert(long long f)
	{
		int h = hash(f);
		return kbuckets[h].insert(static_cast<int>(f));
	}

	// Pure verification - tries sizes kk=k..1 (like python)
	std::vector<std::pair<int, int>> pure_verification(int i)
	{
		std::vector<std::pair<int, int>> answer;

		// get reference to the Kbucket's buckets (assumes getBuckets() exists)
		const std::vector<Bucket> &buckets = kbuckets.at(i).getBuckets();

		// Try decreasing kk from k down to 1
		for (int kk = k; kk >= 1; --kk)
		{
			// Build column vectors a_mat and id_mat of size kk x 1
			Eigen::MatrixXi a_mat(kk, 1);
			Eigen::MatrixXi id_mat(kk, 1);

			// fill from bucket getters (do NOT access private members directly)
			for (int idx = 0; idx < kk; ++idx)
			{
				a_mat(idx, 0) = static_cast<int>(buckets[idx].count);
				id_mat(idx, 0) = static_cast<int>(buckets[idx].id);
			}

			// brute-force candidate g matrices (each is vector<vector<int>> of size kk x kk)
			std::vector<std::vector<std::vector<int>>> g_list = MatrixUtils::brute_force_k2_2d(kk, rc);

			for (const auto &g_mat_vec : g_list)
			{
				// convert to Eigen integer matrix and to double
				Eigen::MatrixXi g_int = vectorToEigen(g_mat_vec, kk, kk);
				Eigen::MatrixXd g_d = g_int.cast<double>();

				// check rank/invertibility (over reals; FullPivLU requires non-integer scalar)
				Eigen::FullPivLU<Eigen::MatrixXd> fu_g(g_d);
				if (fu_g.rank() < kk || !fu_g.isInvertible())
					continue;

				// Solve for c in doubles: g_d * c_d = a_mat
				Eigen::MatrixXd c_d = fu_g.solve(a_mat.cast<double>());

				// Must be near-integer
				Eigen::MatrixXi c_int;
				if (!roundIfClose(c_d, c_int))
					continue;

				// Non-negative counts
				bool any_negative = false;
				for (int r = 0; r < c_int.rows(); ++r)
				{
					if (c_int(r, 0) < 0)
					{
						any_negative = true;
						break;
					}
				}
				if (any_negative)
					continue;

				// Verify exact integer equation: g_int * c_int == a_mat
				Eigen::MatrixXi a_check = g_int * c_int;
				if (!equalInt(a_check, a_mat))
					continue;

				// build gc = g * diag(c_int) (double)
				Eigen::MatrixXd c_diag = c_int.cast<double>().asDiagonal();
				Eigen::MatrixXd gc_d = g_d * c_diag;

				// check invertibility of gc
				Eigen::FullPivLU<Eigen::MatrixXd> fu_gc(gc_d);
				if (fu_gc.rank() < kk || !fu_gc.isInvertible())
					continue;

				// Solve for f_d: gc_d * f_d = id_mat
				Eigen::MatrixXd f_d = fu_gc.solve(id_mat.cast<double>());

				// f must be near-integer
				Eigen::MatrixXi f_int;
				if (!roundIfClose(f_d, f_int))
					continue;

				// verify hash constraint: each recovered flow must hash to bucket i
				bool ok = true;
				for (int idx = 0; idx < f_int.rows(); ++idx)
				{
					int flow_candidate = f_int(idx, 0);
					if (hash(flow_candidate) != i)
					{
						ok = false;
						break;
					}
				}
				if (!ok)
					continue;

				// verify g-consistency: buckets[row].g(flow_candidate, row) == g_int(row,col)
				for (int row = 0; row < kk && ok; ++row)
				{
					for (int col = 0; col < kk; ++col)
					{
						int flow_candidate = f_int(col, 0);
						// Bucket::g must be const-qualified
						if (buckets[row].g(flow_candidate, row) != g_int(row, col))
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
					answer.emplace_back(f_int(j, 0), c_int(j, 0));
				}
				return answer; // return the first valid decoding (same as Python)
			} // end g_list
		} // end kk loop

		// nothing found
		return std::vector<std::pair<int, int>>();
	}

	// Delete (remove) flow occurrences
	void delete_item(long long f, int cnt)
	{
		int h = hash(f);
		kbuckets.at(h).deleteItem(static_cast<int>(f), cnt);
	}
};

#endif // ROWS_H
