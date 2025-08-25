import numpy as np

def matrix_rank_finite_field(matrix, p):
    """
    Finds the rank of a matrix over a finite field modulo p.

    Args:
        matrix: A NumPy array representing the matrix.
        p: The modulus of the finite field.

    Returns:
        The rank of the matrix.
    """
    # Make a copy to avoid modifying the original matrix
    matrix = np.copy(matrix).astype(int)

    rows, cols = matrix.shape
    rank = 0
    for col in range(cols):
        pivot_row = rank
        while pivot_row < rows and matrix[pivot_row, col] % p == 0:
            pivot_row += 1

        if pivot_row < rows:
            # Swap rows
            matrix[[rank, pivot_row]] = matrix[[pivot_row, rank]]

            # Make the pivot element 1 (modulo p)
            pivot_element = matrix[rank, col] % p
            inv_pivot = pow(int(pivot_element), -1, p)
            matrix[rank] = (matrix[rank] * inv_pivot) % p

            # Eliminate other rows
            for i in range(rows):
                if i != rank:
                    factor = matrix[i, col] % p
                    matrix[i] = (matrix[i] - factor * matrix[rank]) % p
            rank += 1

    return rank

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

def brute_force_k2_2d(k):
    length = k * k   # total elements
    for combo in product(range(k), repeat=length):
        # reshape tuple -> k x k matrix
        matrix = [list(combo[i*k:(i+1)*k]) for i in range(k)]
        yield matrix
        
import numpy as np

def inverse_matrix(matrix):
    """
    Compute the inverse of a matrix using NumPy.
    
    Args:
        matrix (list[list[float]] or np.ndarray): The square matrix.
        
    Returns:
        np.ndarray: The inverse matrix.
    """
    mat = np.array(matrix, dtype=float)
    return np.linalg.inv(mat)