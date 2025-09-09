import random
from kbucket import Kbucket
from MrJittacore import brute_force_k2_2d, inverse_matrix
import numpy as np

class Rows:
    def __init__(self, m, p, k, rc, use_modular=False):
        self.kbuckets = [Kbucket(k, p, rc) for _ in range(m)]
        self.p = p
        self.m = m
        self._a = random.randint(1, p - 1)
        self._b = random.randint(0, p - 1)
        self.k = k
        self.rc = rc
        self.use_modular = use_modular  # if True, attempt modular inverses via inverse_matrix(..., p)
        # Cache all brute force matrices for this row
        self.brute_force_matrices = {}
        for kk in range(self.k, 0, -1):
            self.brute_force_matrices[kk] = list(brute_force_k2_2d(kk, self.rc))

    def hash(self, f):
        return ((self._a * f + self._b) % self.p) % self.m

    def insert(self, f):
        h = self.hash(f)
        return self.kbuckets[h].insert(f)

    def pure_verification(self, i):
        """
        Attempt to decode bucket i. Returns list of (flow_id, count) pairs
        for first valid solution found (same behavior as original).
        """
        # get the buckets for this kbucket (list of Bucket instances)
        buckets = self.kbuckets[i].buckets

        # try decreasing kk from self.k down to 1
        for kk in range(self.k, 0, -1):
            # build column vectors a and id from the first kk buckets
            a = np.array([buckets[idx].count for idx in range(kk)], dtype=int).reshape(-1, 1)
            id_vec = np.array([buckets[idx].id for idx in range(kk)], dtype=int).reshape(-1, 1)

            # if all counts are zero, nothing to do
            if np.count_nonzero(a) == 0:
                continue

            # iterate candidate g matrices from cache
            for g_candidate in self.brute_force_matrices[kk]:
                g = np.array(g_candidate, dtype=float)  # use float for numeric inversion
                # quick rank check (floating). If rank < kk skip
                try:
                    rank = np.linalg.matrix_rank(g)
                except Exception:
                    # numerical issue computing rank => skip candidate
                    continue
                if rank < kk:
                    continue

                # Try to invert g (either modular or float)
                try:
                    if self.use_modular:
                        # inverse_matrix expected to support modular inverse when given p
                        inv_g = inverse_matrix(g_candidate, self.p)  # ensure MrJittacore supports this signature
                        inv_g = np.array(inv_g, dtype=float)  # convert to float for further arithmetic
                    else:
                        # float inverse
                        # skip ill-conditioned matrices to reduce numeric instability:
                        cond = np.linalg.cond(g)
                        if not np.isfinite(cond) or cond > 1e12:
                            # ill-conditioned, skip
                            continue
                        inv_g = np.linalg.inv(g)
                    # compute c = inv_g @ a
                    c_d = inv_g @ a.astype(float)

                    # require c to be integer-ish and non-negative
                    if not np.allclose(c_d, np.round(c_d), atol=1e-8):
                        continue
                    c = np.round(c_d).astype(int).reshape(-1, 1)
                    if np.any(c < 0):
                        continue

                    # form diag(c) and attempt to invert gc = g * diag(c)
                    c_diag = np.diagflat(c.flatten())
                    gc = g @ c_diag

                    # check invertibility of gc
                    # skip if gc is ill-conditioned or rank < kk
                    if np.linalg.matrix_rank(gc) < kk:
                        continue
                    cond_gc = np.linalg.cond(gc)
                    if not np.isfinite(cond_gc) or cond_gc > 1e12:
                        continue

                    if self.use_modular:
                        gc_inv = inverse_matrix(gc.astype(int).tolist(), self.p)
                        gc_inv = np.array(gc_inv, dtype=float)
                    else:
                        gc_inv = np.linalg.inv(gc)

                    f_d = gc_inv @ id_vec.astype(float)
                    if not np.allclose(f_d, np.round(f_d), atol=1e-8):
                        continue
                    f = np.round(f_d).astype(int).reshape(-1, 1)

                    # verify that each recovered flow hashes to this bucket i
                    ok = True
                    for idx in range(len(f)):
                        if self.hash(int(f[idx, 0])) != i:
                            ok = False
                            break
                    if not ok:
                        continue

                    # verify g-consistency: bucket.g(flow, row) == g[row, col]
                    for row in range(kk):
                        for col in range(kk):
                            flow_candidate = int(f[col, 0])
                            expected_g = int(round(g[row, col]))
                            # call bucket.g with (flow_candidate, row)
                            if buckets[row].g(flow_candidate, row) != expected_g:
                                ok = False
                                break
                        if not ok:
                            break
                    if not ok:
                        continue

                    # success -> return solution (flow, count) pairs
                    result = [(int(f[j, 0]), int(c[j, 0])) for j in range(kk)]
                    return result

                except Exception:
                    # catch any numeric or modular-inversion failures and skip this candidate
                    continue

        # nothing found
        return []

    def delete(self, f, cnt):
        h = self.hash(f)
        self.kbuckets[h].delete(f, cnt)
