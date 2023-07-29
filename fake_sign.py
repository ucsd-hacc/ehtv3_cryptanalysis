from keys import load_public, load_private
from params import *

import argparse
import math
import subprocess
import sys

from sage.all import (
    ZZ,
    GF, Matrix, identity_matrix, vector, copy,
    random_matrix, random_vector, set_random_seed, randint,
)

def get_a(C, h):
    # Get random a such that Ca = h
    a = vector(GF(Q), C.ncols())

    a[C.nrows():] = random_vector(GF(Q), len(a) - C.nrows())
    C1 = C[:,:C.nrows()]
    C2 = C[:,C.nrows():]

    # We have C1 a1 + C2 a2 = h
    # a1 = C1**-1 (h - C2 a2)
    a[:C.nrows()] = C1**-1 * (h - C2 * a[C.nrows():])
    assert C * a == h
    return a
    

def get_y_small(a):
    # What multiple y of [1, 7] is close to a?
    x = vector(GF(Q), [1, 7])
    a0 = int(a[0])
    for y in range(a0 - 3, a0 + 3 + 1):
        v = y * x
        dist = int(v[1] - a[1])
        if dist <= 3 or dist >= Q - 3:
            break
    return y

def get_yz(T, a):
    # What is the length of the non-triangular bit?
    for i in range(T.ncols()):
        col = T.ncols() - i - 1
        if not T[:-2*(i+1),col].is_zero():
            break
    triangular_columns = i
    non_tri_cols = T.ncols() - triangular_columns

    # Get the nontriangular part of T
    T_ul = T[:T.nrows()-2*triangular_columns,:non_tri_cols]

    a_top = a[:T_ul.nrows()]
    # Find y_top such that a_top = T_ul * y_top + z_top
    # for z bounded
    L = Matrix(ZZ, T_ul.nrows() + 1, T_ul.nrows() + 1)
    T_ul_ech = T_ul.T.echelon_form()
    m = T_ul_ech.nrows()
    n = T_ul_ech.ncols()
    L[:m,:n] = T_ul_ech
    L[m:n,m:n] = identity_matrix(ZZ,n-m) * Q

    # CVP embedding
    cvp_embed = 9
    L[-1,:n] = a_top
    L[-1,-1] = cvp_embed

    L = L.LLL()
    if L[-1,-1] == -cvp_embed:
        L[-1] *= -1
    assert L[-1,-1] == cvp_embed

    z_top = vector(GF(Q), L[-1,:n].list())
    y_top = T_ul.solve_right(a_top - z_top)

    # Get the triangular part of T
    y = vector(GF(Q), T.ncols())
    y[:len(y_top)] = y_top
    z = copy(a) - T*y

    for i in range(len(y) - len(y_top)):
        ind = len(z_top) + 2 * i
        a_sub = z[ind:ind+2]

        # Get value of y that fits best
        yi = get_y_small(a_sub)
        z -= yi * vector(T[:,len(y_top) + i])
        y[len(y_top) + i] = yi

    # Now have candidate y, z
    z = a - T*y
    for zi in z.list():
        zi = int(zi)
        assert zi <= 3 or zi >= Q - 3
    return y, z

def eht_hash(msg):
    # Return h corresponding to msg.
    p = subprocess.Popen(["c_utils/eht_hash"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = p.communicate(msg)
    h = list(bytearray(stdout))
    return vector(GF(Q),h)

def encode_mx(msg, x):
    size = int(math.ceil(len(x) * math.log(Q) / math.log(256)))

    sm = [0] * size

    for i in range(len(x)):
        carry = int(x[i])
        for j in range(size - 1, -1, -1):
            tmp = sm[j] * Q + carry;
            sm[j] = tmp % 256
            carry = tmp // 256

    sm = bytes(bytearray(sm)) + msg
    return sm

def sign(priv, msg):
    Zq = GF(Q)

    C = priv.C
    T = priv.T
    B = priv.B
    h = eht_hash(msg)

    set_random_seed(3)
    while True:
        # Generate a such that C * a = h
        a = get_a(C, h)

        # Generate y, z such that a = Ty + z
        # and z is bounded
        y, z = get_yz(T, a)

        e = C * z
        e_int = [
            int(e[i]) for i in range(len(e))
        ]
        # At least l entries of e are at most s
        count = sum([
            1 if ei <= 13 or ei >= Q - 13 else 0 for ei in e_int
        ])
        if count >= 451:
            break
    x = B * y
    return encode_mx(msg, x)

def main():
    parser = argparse.ArgumentParser(
        description='Run the private key recovery attack from knowledge of columns.'
    )
    parser.add_argument('priv', type=str, help="Fake private key")
    parser.add_argument('msg', type=str, help="Message to sign")
    args = parser.parse_args()

    priv = load_private(args.priv, real=False)

    msg = args.msg.encode()

    sig = sign(priv, msg)
    sys.stdout.buffer.write(sig)

if __name__ == "__main__":
    main()
