#include "./jittatcore.h"
#include <bits/stdc++.h>
#include <vector>
#include <random>
#include <utility>
#include <cmath>
#include <Eigen/Dense>
#include "util/murmur3.h"
using namespace std;

int main()
{
	vector<vector<int>> A = {
		{1, 2, 3},
		{0, 1, 4},
		{5, 6, 0}};
	int rank = MatrixUtils::find_rank(A, 7);
	cout << "Rank of A mod 7: " << rank << "\n";
	vector<vector<int>> A_inv;
	try
	{
		A_inv = MatrixUtils::inverse_matrix(A, 7);
	}
	catch (const std::exception &e)
	{
		std::cerr << "Error: " << e.what() << std::endl;
		return 1;
	}
	cout << "A_inv:\n";
	for (const auto &row : A_inv)
	{
		for (const auto &val : row)
		{
			cout << val << " ";
		}
		cout << "\n";
	}
}