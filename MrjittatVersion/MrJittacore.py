from itertools import product
import numpy as np

# primes must have at least k * rc elements (or k*rc + max_offset)
PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,
          101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,179,181,
          191,193,197,199,211,223,227,229,233,239,241,251,257,263,269,271,277,281]

def brute_force_k2_2d(k, rc):
    """
    Generate k x k matrices where each entry is chosen from 0..rc-1,
    then mapped through prime[index + i*rc] as in your original code.

    WARNING: search space size = rc^(k*k) — can be enormous.
    """
    length = k * k
    # check primes length
    needed = k * rc
    if needed > len(PRIMES):
        raise ValueError(f"PRIMES list too small: need at least {needed} primes, have {len(PRIMES)}")

    for combo in product(range(0, rc), repeat=length):
        mat_indices = [list(combo[i*k:(i+1)*k]) for i in range(k)]
        # map indices to primes
        matrix = [[PRIMES[mat_indices[i][j] + i * rc] for j in range(k)] for i in range(k)]
        yield matrix


# ---------- modular inverse for matrices via Gauss-Jordan mod p ----------
def matrix_mod_inverse(A, p):
    """
    Compute inverse of integer matrix A modulo prime p.
    A: list of lists or 2D numpy array (square)
    returns: numpy.ndarray (dtype=int) of shape (n,n) with values in 0..p-1
    raises: ValueError if singular modulo p
    """
    A = np.array(A, dtype=int) % p
    n = A.shape[0]
    if A.shape[0] != A.shape[1]:
        raise ValueError("Only square matrices can be inverted")

    # build augmented matrix [A | I]
    aug = np.hstack([A.copy(), np.eye(n, dtype=int)])
    # perform Gauss-Jordan elimination modulo p
    for col in range(n):
        # find pivot row with non-zero in this column
        pivot = None
        for r in range(col, n):
            if aug[r, col] % p != 0:
                pivot = r
                break
        if pivot is None:
            raise ValueError("Matrix is singular modulo p")

        # swap pivot row into place
        if pivot != col:
            aug[[col, pivot]] = aug[[pivot, col]]

        # normalize pivot row: multiply by inv(pivot_val) mod p
        pivot_val = int(aug[col, col] % p)
        inv_pivot = pow(pivot_val, p - 2, p)  # p should be prime; uses Fermat
        aug[col, :] = (aug[col, :] * inv_pivot) % p

        # eliminate other rows
        for r in range(n):
            if r == col:
                continue
            factor = int(aug[r, col] % p)
            if factor != 0:
                aug[r, :] = (aug[r, :] - factor * aug[col, :]) % p

    inv = aug[:, n:] % p
    return inv.astype(int)


def inverse_matrix(matrix, p=None):
    """
    If p is provided -> return modular inverse over GF(p) as numpy int array.
    If p is None -> return standard numpy.linalg.inv (float).
    """
    mat = np.array(matrix)
    if p is None:
        return np.linalg.inv(mat.astype(float))
    else:
        return matrix_mod_inverse(mat, p)
