import argparse
from keys import load_public, load_private
import json
from sage.all import (
    GF, Matrix, identity_matrix, vector,
    random_matrix, set_random_seed, randint,
)

class EHTRecoveryFromColumns:
    def __init__(self, pub, C_cols, priv=None, verbose=False):
        self.pub = pub
        self.verbose = verbose

        self.A = self.pub.A
        self.k = 2
        self.m = self.A.nrows()
        self.n = self.A.ncols()
        self.q = 47
        self.Zq = GF(self.q)

        self.C_cols = [vector(self.Zq, Ci) for Ci in C_cols]

    def log(self, *args, **kwargs):
        if self.verbose:
            print(*args, **kwargs)

    def build_C_right(self, C_cols_known):
        C_right = Matrix(self.Zq, self.m, len(C_cols_known))
        for i, (ind, sgn) in enumerate(C_cols_known):
            C_right[:,i] = sgn * self.C_cols[ind]
        return C_right

    def recover_next_column_pair_of_C(self, C_cols_known=[]):
        # Given the known columns, return all possible values
        # which include the next pair of known columns.
        
        l = len(C_cols_known) // 2
        # We know CT = AB, and we know 2l of the rightmost columns of C.
        # We wish to determine the left kernel K of the rightmost columns of C
        # so that KC has zeros in the last 2l columns. This makes it so
        # KCT does not depend on the last l rows of T.
        #
        # Column k-1-l of KCT only depends on columns 2(k-l-1) and 2(k-l-1) + 1
        # of C (which are unkown) and column k-l-1 of T (which is known except
        # for the last l rows). Because KCT = KAB, column k-1-l of KCT is in
        # the column span of A (which is known).
        #
        # We use a meet-in-the-middle attack to determine which columns of C
        # are correct for these indices. We want to find indices i, j such that
        # K * sgn_i * C_cols[i] * 1 + K * sgn_j * C_cols[j] * 7 \in span(KA)
        # WLOG, we can assume sgn_j = 1.
        # We compute v_i = K*C_cols[i] and subtract columns of KA until the leading
        # entries of v_i are all 0. Then, we just need to find i, j, sgn_i such that
        #     sgn_i * v_i + 7 * v_j = 0
        # which we can do with a meet-in-the-middle attack.
        if l > 0:
            C_right = self.build_C_right(C_cols_known)
            K = Matrix(C_right.left_kernel().basis())
        else:
            K = identity_matrix(self.Zq, self.m)

        KA = K * self.A

        # Build matrix of remaining candidates
        KC_candidates = Matrix(self.Zq, K.nrows(), len(self.C_cols) - 2*l)
        ind = 0
        index_map_original_C_cols = []
        for i, Ci in enumerate(self.C_cols):
            if i in [rec for rec, _ in C_cols_known]:
                # Already used i
                continue
            KC_candidates[:,ind] = K * self.C_cols[i]
            index_map_original_C_cols += [i]
            ind += 1
        assert ind == len(self.C_cols) - 2*l

        # Zero out the top entries of KC_candidates
        # Get column echelon form of KA
        KA_echelon = KA.T.echelon_form().T
        ncols = KA_echelon.rank()
        KA_echelon = KA_echelon[:,:ncols]
        inds_to_clear = []
        for i in range(ncols):
            j = 0
            while j < KA_echelon.nrows() and KA_echelon[j,i] == 0:
                j += 1
            assert j != KA_echelon.nrows()
            assert KA_echelon[j,i] == 1
            inds_to_clear += [j]

        KC_candidates -= KA_echelon * KC_candidates[inds_to_clear]
        assert KC_candidates[:KA_echelon.nrows()-KA_echelon.ncols()].is_zero()

        # Get list of candidates
        v_s = KC_candidates.columns()

        # Do meet in the middle attack.
        for j in range(len(v_s)):
            v_j = v_s[j]

            for sgn_i in [-1, 1]:
                v_i = sgn_i * -7 * v_j
                if v_i in v_s:
                    # sgn_i * v_i = -7 * v_j
                    i = v_s.index(v_i)
                    if i == j:
                        continue

                    # Map back to indices in self.C_cols
                    I = index_map_original_C_cols[i]
                    J = index_map_original_C_cols[j]

                    yield [(I, sgn_i), (J, 1)] + C_cols_known
        return None

    def recover_column_order_of_C(self, C_cols_known=[]):
        # Recursive call to determine the order of columns in C.
        # Returns a list of 2*l tuples (ind, sgn) corresponding to the
        # rightmost 2*l columns of C, as specified by their index in
        # self.C_cols and their sign.
        assert self.k == 2

        if len(C_cols_known) >= self.k * (self.m - self.n - 1):
            # We cannot recover any more columns than this
            return C_cols_known

        for next_C_cols_known in self.recover_next_column_pair_of_C(C_cols_known):
            self.log(f"Found pair for step {len(C_cols_known)//2}: {next_C_cols_known[:2]}")
            all_C_cols_known = self.recover_column_order_of_C(next_C_cols_known)
            if all_C_cols_known is None:
                # We guessed wrong. Keep trying.
                continue
            else:
                return all_C_cols_known

        return None

    def recover_T(self, C):
        # Once again, recall we have CT = AB, and depending on the choice of left kernel K,
        # KCT = KAB with some of the final rows of T having no effect on the matrix multiplication.
        # Our attack is thus to compute KC such that KCT only depends on a single pair of
        # (unknown) rows below the diagonal of T. For each column, we could brute force
        # the two entries in the unknown row and check if the column in KCT is in the span of A.
        #
        # As before, we can optimize this process. Instead of brute forcing a pair of values
        # from 0 to 47, we can WLOG simplify this to a recovering a single value from 0 to 47.
        # In the intersection of the two unknown rows of T and the unknown column, we have
        #     [u1]
        #     [u2]
        # as unknowns. But we know that there is a column in T to the right of this unknown
        # column where the entries in the unknown row are on the diagonal and are therefore
        #     [ 1]
        #     [ 7].
        # WLOG, we can assume that the entries corresponding to u1 in T are 0. If this were
        # not the case, we could do column operations to manipulate T (and do the corresponding
        # row operations to B^{-1} such that TB^{-1} is constant) until u1 = 0.
        # The unknowns now are
        #     [ 0]
        #     [u']
        # so we only need to recover u'.
        #
        # We thus are searching for scalar u' such that a particular column of KCT is in the
        # linear span of A. Do this.
        assert self.k == 2
        l = C.ncols() // self.k
        row_pairs_remaining = l

        # C and T are not full size, but they do not need to be for this step
        T = Matrix(self.Zq, 2 * l, l)

        while row_pairs_remaining > 0:
            row = 2 * (l - row_pairs_remaining)

            if row_pairs_remaining > 1:
                C_right = C[:,-(row_pairs_remaining-1)*2:]
                K = Matrix(C_right.left_kernel().basis())
            else:
                K = identity_matrix(self.Zq, C.nrows())
            KC = K * C

            # Get column echelon form of KA
            KA = K * self.A
            KA_echelon = KA.T.echelon_form().T
            ncols = KA_echelon.rank()
            KA_echelon = KA_echelon[:,:ncols]
            inds_to_clear = []
            for i in range(ncols):
                j = 0
                while j < KA_echelon.nrows() and KA_echelon[j,i] == 0:
                    j += 1
                assert j != KA_echelon.nrows()
                assert KA_echelon[j,i] == 1
                inds_to_clear += [j]

            # Diagonal is known
            T[row, l - row_pairs_remaining] = 1
            T[row + 1, l - row_pairs_remaining] = 7

            for col in range(l - row_pairs_remaining):
                # Recover subdiagonal entries in row
                # The column in KCT we care about is
                # (KCT)[:,col] = (KC[:,:row+1])(T[:,col])
                # = KC[:,:row] * T[:row, col] + KC[:,row]T[row, col] + KC[:,row+1]T[row + 1, col]
                # = KC[:,:row] * T[:row, col] + 0 + KC[:,row+1]u1
                T[row, col] = 0
                T[row+1, col] = 0
                KCT_col = KC * T[:,col]
                v = KC[:,row+1]

                # Reduce KCT_col by columns of KA
                KCT_col -= KA_echelon * KCT_col[inds_to_clear]

                # Reduce v by columns of KA
                v -= KA_echelon * v[inds_to_clear]

                # What value of u will satisfy
                #     0 = KCT_col + u * v
                v_nonzero_ind = 0
                assert not v.is_zero()
                while v[v_nonzero_ind] == 0:
                    v_nonzero_ind += 1

                u = -KCT_col[v_nonzero_ind,0] * v[v_nonzero_ind,0]**-1

                assert (KCT_col + u * v).is_zero()
                T[row,col] = 0
                T[row+1,col] = u

            self.log(f"Remaining rows: {row_pairs_remaining}")
            row_pairs_remaining -= 1
        return T

    def fill_in_remainder(self, C_part, T_part):
        # Come up with C, T, B such that C is sparse, T is lower triangular
        # (except for a bit at the top), B is invertible, and CT = AB.
        assert self.k == 2
        l = C_part.ncols() // 2

        # Make slightly larger than square to allow flexibility
        # when making signatures. We want more than one a to satisfy Ca = h.
        C = Matrix(self.Zq, self.m, self.m + 1)
        C[:,-2*l:] = C_part

        T = Matrix(self.Zq, self.m + 1, self.n)
        T[-2*l:,-l:] = T_part

        B = Matrix(self.Zq, self.n, self.n)
        # Some of B can be determined from what we have already,
        # since we know the rightmost l columns of CT, which match
        # the rightmost columns of AB.
        B[:,-l:] = self.A.solve_right((C*T)[:,-l:])

        # Randomly fill in the rest until B is invertible
        set_random_seed(3)
        while not B.is_invertible():
            B[:,:-l] = random_matrix(self.Zq, self.n, self.n-l)

        # Randomly add entries to the unknown part of C until it's invertible
        while not C[:,:self.m].is_invertible():
            row = randint(0, C.nrows() - 1)
            col = randint(0, C.ncols() - 2*l - 1)
            C[row, col] += 1

        # Solve for remaining entries of T.
        # This is not upper triangular, but it does not affect our ability
        # to solve CVP in T.
        # CT = AB
        T[:,:T.ncols()-l] = C.solve_right((self.A * B)[:,:T.ncols()-l])

        return C, T, B

    def key_as_json(self, C, T, B):
        data = {}
        C = [[int(cij) for cij in Ci] for Ci in C.rows()]
        T = [[int(tij) for tij in Ti] for Ti in T.rows()]
        B = [[int(bij) for bij in Bi] for Bi in B.rows()]

        data["C"] = C
        data["T"] = T
        data["B"] = B
        return json.dumps(data)

    def solve(self):
        column_order = self.recover_column_order_of_C()
        C_part = self.build_C_right(column_order)
        T_part = self.recover_T(C_part)
        C, T, B = self.fill_in_remainder(C_part, T_part)

        # Columns of t not lower triangular
        key = self.key_as_json(C, T, B)

        return key

def main():
    parser = argparse.ArgumentParser(
        description='Run the private key recovery attack from knowledge of columns.'
    )
    parser.add_argument('pub', type=str, help="Public key generated by eht_print_pk")
    parser.add_argument('cols', type=str, help="File containing columns of C")
    parser.add_argument('priv', type=str, help="Where to write private key")
    parser.add_argument('--verbose', '-v', action='store_true', help="enable verbose output")
    args = parser.parse_args()

    pub = load_public(args.pub)
    
    with open(args.cols) as f:
        cols = []
        for line in f:
            col = json.loads(line)
            cols += [col]
    with open(args.priv, "w") as g:
        # Make sure we can write output
        pass

    #pub, cols, priv = gen_bd()

    problem = EHTRecoveryFromColumns(pub, cols, verbose=args.verbose)

    priv = problem.solve()

    print("Key recovery successful.")
    with open(args.priv, "w") as g:
        g.write(priv)
    

if __name__ == "__main__":
    main()
