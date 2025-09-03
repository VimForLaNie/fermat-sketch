#ifndef ROWS_H
#define ROWS_H

#include <vector>
#include <random>
#include <utility>
#include <cmath>
#include <Eigen/Dense>

#include "./kbucket.h"	  // must provide Kbucket and getBuckets()
#include "./jittatcore.h" // must provide MatrixUtils::brute_force_k2_2d(...)

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

	// Helper: round Eigen::MatrixXd to Eigen::MatrixXi
	static inline Eigen::MatrixXi roundMatrix(const Eigen::MatrixXd &mat)
	{
		Eigen::MatrixXi out(mat.rows(), mat.cols());
		for (int i = 0; i < mat.rows(); ++i)
			for (int j = 0; j < mat.cols(); ++j)
				out(i, j) = static_cast<int>(std::llround(mat(i, j)));
		return out;
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
		// result: vector of (flow_id, count)
		std::vector<std::pair<int, int>> answer;

		// get reference to the Kbucket's buckets
		const std::vector<Bucket> &buckets = kbuckets.at(i).getBuckets();

		// Try decreasing kk from k down to 1
		for (int kk = k; kk >= 1; --kk)
		{
			// Build column vectors a_mat and id_mat of size kk x 1
			Eigen::MatrixXi a_mat(kk, 1);
			Eigen::MatrixXi id_mat(kk, 1);

			// fill from bucket getters (use getters, not public fields)
			for (int idx = 0; idx < kk; ++idx)
			{
				a_mat(idx, 0) = static_cast<int>(buckets[idx].count);
				id_mat(idx, 0) = static_cast<int>(buckets[idx].id);
			}

			// brute-force candidate g matrices (each is vector<vector<int>> of size kk x kk)
			std::vector<std::vector<std::vector<int>>> g_list = MatrixUtils::brute_force_k2_2d(kk, rc);

			for (const auto &g_mat_vec : g_list)
			{
				// convert to Eigen matrix
				Eigen::MatrixXi g = vectorToEigen(g_mat_vec, kk, kk);

				// check rank
				if (g.cast<double>().fullPivLu().rank() < kk)
					continue;

				// Solve c = inv(g) * a
				// use double for numeric computations then round/validate
				Eigen::MatrixXd g_d = g.cast<double>();
				// guard: if g is ill-conditioned inverse may be unstable; try-catch anyway
				try
				{
					Eigen::MatrixXd g_inv = g_d.inverse();
					Eigen::MatrixXd c_d = g_inv * a_mat.cast<double>();

					// integer & non-negative check (round)
					Eigen::MatrixXi c_int = roundMatrix(c_d);
					bool any_negative = false;
					for (int r = 0; r < c_int.rows(); ++r)
						if (c_int(r, 0) < 0)
						{
							any_negative = true;
							break;
						}
					if (any_negative)
						continue;

					// build diag(c) and compute f = inv(G * diag(c)) * id
					Eigen::MatrixXd c_diag = c_int.cast<double>().asDiagonal();
					Eigen::MatrixXd gc = g_d * c_diag;

					// need gc invertible
					if (Eigen::FullPivLU<Eigen::MatrixXd>(gc).rank() < kk)
						continue;

					Eigen::MatrixXd gc_inv = gc.inverse();
					Eigen::MatrixXd f_d = gc_inv * id_mat.cast<double>();

					Eigen::MatrixXi f_int = roundMatrix(f_d);

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

					// verify g-consistency: buckets[row].g(flow_candidate, row) == g(row,col)
					for (int row = 0; row < kk && ok; ++row)
					{
						for (int col = 0; col < kk; ++col)
						{
							int flow_candidate = f_int(col, 0);
							// Bucket::g must be const-qualified
							if (buckets[row].g(flow_candidate, row) != g(row, col))
							{
								ok = false;
								break;
							}
						}
					}
					if (!ok)
						continue;

					// success: collect (flow, count) pairs
					answer.reserve(static_cast<size_t>(kk));
					for (int j = 0; j < kk; ++j)
					{
						answer.emplace_back(f_int(j, 0), c_int(j, 0));
					}
					return answer; // same behavior as Python: return first valid decoding
				}
				catch (const std::exception &)
				{
					// numeric error / inverse failure -> skip candidate
					continue;
				}
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
