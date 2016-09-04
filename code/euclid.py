import numpy as np
from numba import jit

def pdist_numpy(xs):
    return np.sqrt(((xs[:,None,:] - xs)**2).sum(-1))


pdist_numba = jit(pdist_numpy)

def pdist_python(xs):
    n, p = xs.shape
    D = np.empty((n, n), dtype=np.float)
    for i in range(n):
        for j in range(n):
            s = 0.0
            for k in range(p):
                tmp = xs[i,k] - xs[j,k]
                s += tmp * tmp
            D[i, j] = s**0.5
    return D

pdist_python_numba = jit(pdist_python)

if __name__ == "__main__":
    X = np.random.randn(5, 100)
    dist1 = pdist_numba(X)
    dist2 = pdist_python_numba(X)
    assert np.allclose(dist1, dist2)
