#ifndef MATRIX_UTILS_H
#define MATRIX_UTILS_H

#include <vector>
#include <iostream>
#include <stdexcept>
#include <algorithm>
#include <numeric>
#include <cmath>
#include "bucket.h"
#include "./util/murmur3.h"
using Matrix = std::vector<std::vector<int>>;

namespace MatrixUtils
{

	// Compute rank of a matrix over finite field (mod p)
	int matrix_rank_finite_field(std::vector<std::vector<int>> matrix, long long p)
	{
		int rows = matrix.size();
		int cols = matrix[0].size();
		int rank = 0;

		for (int col = 0; col < cols; col++)
		{
			int pivot_row = rank;
			while (pivot_row < rows && matrix[pivot_row][col] % p == 0)
			{
				pivot_row++;
			}

			if (pivot_row < rows)
			{
				// Swap rows
				std::swap(matrix[rank], matrix[pivot_row]);

				// Make pivot element 1 (mod p)
				int pivot_element = (matrix[rank][col] % p + p) % p;
				int inv_pivot = -1;

				// Find modular inverse of pivot_element mod p
				for (int x = 1; x < p; x++)
				{
					if ((pivot_element * x) % p == 1)
					{
						inv_pivot = x;
						break;
					}
				}
				if (inv_pivot == -1)
					// throw std::runtime_error("No modular inverse found!");
					return rank; // signal no inverse

				for (int j = 0; j < cols; j++)
				{
					matrix[rank][j] = (matrix[rank][j] * inv_pivot) % p;
				}

				// Eliminate other rows
				for (int i = 0; i < rows; i++)
				{
					if (i != rank)
					{
						int factor = matrix[i][col] % p;
						for (int j = 0; j < cols; j++)
						{
							matrix[i][j] = (matrix[i][j] - factor * matrix[rank][j]) % p;
							if (matrix[i][j] < 0)
								matrix[i][j] += p;
						}
					}
				}
				rank++;
			}
		}
		return rank;
	}

	// Brute force k^2 matrix generator
	std::vector<std::vector<std::vector<int>>> brute_force_k2_2d(int k, int rc)
	{

		std::vector<std::vector<std::vector<int>>> results;

		int length = k * k;
		std::vector<int> combo(length, 0);

		while (true)
		{
			// Construct matrix from combo
			std::vector<std::vector<int>> matrix(k, std::vector<int>(k));
			for (int i = 0; i < k; i++)
			{
				for (int j = 0; j < k; j++)
				{
					int idx = combo[i * k + j];
					matrix[i][j] = PRIME_LIST[idx + i * rc];
				}
			}
			results.push_back(matrix);

			// Increment combo
			int pos = length - 1;
			while (pos >= 0 && combo[pos] == rc - 1)
			{
				combo[pos] = 0;
				pos--;
			}
			if (pos < 0)
				break;
			combo[pos]++;
		}

		return results;
	}

	// Matrix inverse (optionally mod p)
	std::vector<std::vector<int>> inverse_matrix(const std::vector<std::vector<int>> &matrix, int p = -1)
	{
		int n = matrix.size();
		std::vector<std::vector<int>> A = matrix;
		std::vector<std::vector<int>> I(n, std::vector<int>(n, 0));

		for (int i = 0; i < n; i++)
			I[i][i] = 1;

		for (int i = 0; i < n; i++)
		{
			int pivot = A[i][i];
			if (p != -1)
				pivot = (pivot % p + p) % p;

			if (pivot == 0)
				// throw std::runtime_error("Matrix is singular!");
				return std::vector<std::vector<int>>(); // signal no inverse

			int inv_pivot = -1;
			if (p != -1)
			{
				for (int x = 1; x < p; x++)
				{
					if ((pivot * x) % p == 1)
					{
						inv_pivot = x;
						break;
					}
				}
				if (inv_pivot == -1)
					// throw std::runtime_error("No modular inverse found!");
					return std::vector<std::vector<int>>(); // signal no inverse
			}

			for (int j = 0; j < n; j++)
			{
				if (p == -1)
				{
					A[i][j] /= pivot;
					I[i][j] /= pivot;
				}
				else
				{
					A[i][j] = (A[i][j] * inv_pivot) % p;
					I[i][j] = (I[i][j] * inv_pivot) % p;
				}
			}

			for (int k2 = 0; k2 < n; k2++)
			{
				if (k2 != i)
				{
					int factor = A[k2][i];
					for (int j = 0; j < n; j++)
					{
						if (p == -1)
						{
							A[k2][j] -= factor * A[i][j];
							I[k2][j] -= factor * I[i][j];
						}
						else
						{
							A[k2][j] = (A[k2][j] - factor * A[i][j]) % p;
							I[k2][j] = (I[k2][j] - factor * I[i][j]) % p;
							if (A[k2][j] < 0)
								A[k2][j] += p;
							if (I[k2][j] < 0)
								I[k2][j] += p;
						}
					}
				}
			}
		}
		return I;
	}

	std::vector<std::vector<int>> matmul_mod(const Matrix &A, const Matrix &B, long long p)
	{
		if (p <= 0)
			throw std::invalid_argument("modulus p must be > 0");
		std::size_t n = A.size();
		if (n == 0)
			return Matrix{};
		std::size_t m = A[0].size();
		std::size_t q = B.size();
		if (m != q)
			throw std::invalid_argument("A columns must equal B rows");
		std::size_t r = B[0].size();

		// allocate result filled with 0
		Matrix C(n, std::vector<int>(r, 0));
		for (std::size_t i = 0; i < n; ++i)
		{
			if (A[i].size() != m)
				throw std::invalid_argument("A is ragged");
			for (std::size_t k = 0; k < m; ++k)
			{
				if (B[k].size() != r)
					throw std::invalid_argument("B is ragged");
				int aik = A[i][k];
				if (aik == 0)
					continue; // small opt
				for (std::size_t j = 0; j < r; ++j)
				{
					// use 64-bit intermediate to avoid overflow
					int64_t prod = int64_t(aik) * int64_t(B[k][j]);
					int64_t sum = int64_t(C[i][j]) + (prod % p);
					sum %= p;
					if (sum < 0)
						sum += p;
					C[i][j] = static_cast<int>(sum);
				}
			}
		}
		return C;
	}

	std::vector<int> mat_vec_mul(const std::vector<std::vector<int>> &M, const std::vector<int> &v, long long pmod)
	{
		int n = (int)M.size();
		std::vector<int> out(n, 0);
		for (int r = 0; r < n; ++r)
		{
			long long acc = 0;
			for (int c = 0; c < n; ++c)
			{
				long long prod = 1LL * M[r][c] * v[c];
				if (pmod != -1)
				{
					prod %= pmod;
				}
				acc += prod;
				if (pmod != -1)
				{
					acc %= pmod;
				}
			}
			if (pmod != -1)
			{
				acc %= pmod;
				if (acc < 0)
					acc += pmod;
			}
			out[r] = static_cast<int>(acc);
		}
		return out;
	}

	long long modinv(long long a, long long p)
	{
		long long t = 0, newt = 1;
		long long r = p, newr = a % p;
		while (newr != 0)
		{
			long long q = r / newr;
			t = t - q * newt;
			std::swap(t, newt);
			r = r - q * newr;
			std::swap(r, newr);
		}
		if (r > 1)
			throw std::runtime_error("No modular inverse");
		if (t < 0)
			t += p;
		return t;
	}

	int find_rank(const std::vector<std::vector<int>> &M, long long p)
	{
		if (M.empty())
			return 0;
		int rows = (int)M.size();
		int cols = (int)M[0].size();

		// Copy to long long (to avoid overflow)
		std::vector<std::vector<long long>> A(rows, std::vector<long long>(cols));
		for (int i = 0; i < rows; i++)
			for (int j = 0; j < cols; j++)
			{
				long long val = M[i][j] % p;
				if (val < 0)
					val += p;
				A[i][j] = val;
			}

		int rank = 0;
		for (int col = 0; col < cols && rank < rows; col++)
		{
			// Find pivot row (with nonzero entry)
			int pivot = -1;
			for (int r = rank; r < rows; r++)
			{
				if (A[r][col] != 0)
				{
					pivot = r;
					break;
				}
			}
			if (pivot == -1)
				continue;

			// Swap pivot row into place
			if (pivot != rank)
				std::swap(A[pivot], A[rank]);

			// Normalize pivot to 1
			long long inv_piv = modinv(A[rank][col], p);
			for (int j = col; j < cols; j++)
			{
				A[rank][j] = (A[rank][j] * inv_piv) % p;
			}

			// Eliminate rows below and above
			for (int r = 0; r < rows; r++)
			{
				if (r == rank)
					continue;
				if (A[r][col] != 0)
				{
					long long factor = A[r][col];
					for (int j = col; j < cols; j++)
					{
						A[r][j] = (A[r][j] - factor * A[rank][j]) % p;
						if (A[r][j] < 0)
							A[r][j] += p;
					}
				}
			}

			rank++;
		}
		return rank;
	}

}

#endif // MATRIX_UTILS_H
