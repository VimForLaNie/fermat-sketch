#ifndef MATRIX_UTILS_H
#define MATRIX_UTILS_H

#include <vector>
#include <iostream>
#include <stdexcept>
#include <algorithm>
#include <numeric>
#include <cmath>

namespace MatrixUtils
{

	// Compute rank of a matrix over finite field (mod p)
	int matrix_rank_finite_field(std::vector<std::vector<int>> matrix, int p)
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
					throw std::runtime_error("No modular inverse found!");

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
		std::vector<int> primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
								   31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
								   73, 79, 83, 89, 97};

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
					matrix[i][j] = primes[idx + i * rc];
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
				throw std::runtime_error("Matrix is singular!");

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
					throw std::runtime_error("No modular inverse found!");
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

}

#endif // MATRIX_UTILS_H
