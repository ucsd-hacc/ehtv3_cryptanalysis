import json
from sage.all import Matrix, GF
from params import *

def load_public(fname):
    with open(fname) as f:
        data = json.loads(f.read())
        
    Zq = GF(Q)
    A = Matrix(Zq, data["A"])
    assert A.nrows() == M
    assert A.ncols() == N
    return EHTPublic(A)

def load_private(fname, real=True):
    with open(fname) as f:
        data = json.loads(f.read())

    Zq = GF(Q)
    C = Matrix(Zq, data["C"])
    if real:
        assert C.nrows() == M
        assert C.ncols() == M + D

    T = Matrix(Zq, data["T"])
    if real:
        assert T.nrows() == M + D
        assert T.ncols() == N

    B = Matrix(Zq, data["B"])
    if real:
        assert B.nrows() == N
        assert B.ncols() == N

    return EHTPrivate(C, T, B)

class EHTPrivate:
    def __init__(self, C, T, B):
        self.C = C
        self.T = T
        self.B = B

class EHTPublic:
    def __init__(self, A):
        self.A = A
