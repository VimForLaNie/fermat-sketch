import numpy as np

# def matrix_rank_finite_field(matrix, p):
#     """
#     Finds the rank of a matrix over a finite field modulo p.

#     Args:
#         matrix: A NumPy array representing the matrix.
#         p: The modulus of the finite field.

#     Returns:
#         The rank of the matrix.
#     """
#     # Make a copy to avoid modifying the original matrix
#     matrix = np.copy(matrix).astype(int)

#     rows, cols = matrix.shape
#     rank = 0
#     for col in range(cols):
#         pivot_row = rank
#         while pivot_row < rows and matrix[pivot_row, col] % p == 0:
#             pivot_row += 1

#         if pivot_row < rows:
#             # Swap rows
#             matrix[[rank, pivot_row]] = matrix[[pivot_row, rank]]

#             # Make the pivot element 1 (modulo p)
#             pivot_element = matrix[rank, col] % p
#             inv_pivot = pow(int(pivot_element), -1, p)
#             matrix[rank] = (matrix[rank] * inv_pivot) % p

#             # Eliminate other rows
#             for i in range(rows):
#                 if i != rank:
#                     factor = matrix[i, col] % p
#                     matrix[i] = (matrix[i] - factor * matrix[rank]) % p
#             rank += 1

#     return rank

# Example Usage:
# matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
# p = 3
# rank = matrix_rank_finite_field(matrix, p)
# print(f"The rank of the matrix modulo {p} is: {rank}")

# matrix2 = np.array([[1, 1, 0], [0, 1, 1], [1, 0, 1]])
# p2 = 2
# rank2 = matrix_rank_finite_field(matrix2, p2)
# print(f"The rank of the matrix modulo {p2} is: {rank2}")

from itertools import product

def brute_force_k2_2d(k,rc):
    length = k * k
    prime = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
    for combo in product(range(0, rc), repeat=length):  # 1..k instead of 0..k-1
    # for combo in product([2,3,5,7,11,13,17,19][:rc], repeat=length):  # 1..k instead of 0..k-1
        matrix = [list(combo[i*k:(i+1)*k]) for i in range(k)]
        matrix = [[prime[matrix[i][j] + i * rc] for j in range(k)] for i in range(k)]
        # print(f"Trying matrix: {matrix}")
        yield matrix
        
import numpy as np

def inverse_matrix(matrix, p = None):
    """
    Compute the inverse of a matrix using NumPy.
    
    Args:
        matrix (list[list[float]] or np.ndarray): The square matrix.
        
    Returns:
        np.ndarray: The inverse matrix.
    """
    if p is not None :
        matrix = np.array(matrix, dtype=int) % p
        inv = np.linalg.inv(matrix).astype(int) % p
        for i in range(len(inv)) :
            for j in range(len(inv)) :
                inv[i][j] = inv[i][j] % p
        return inv
    else :
        return np.linalg.inv(matrix)