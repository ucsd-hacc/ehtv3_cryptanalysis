from partial_key_recovery import EHTRecoveryFromColumns
from keys import load_public, load_private

import numpy as np
import json

def test_validity(priv, pub):
    if (priv.C * priv.T - pub.A * priv.B).is_zero():
        print("The public and private key are valid")
    else:
        print("Error: CT != AB")
        return False
    return True

def test_recovery_from_columns(priv, pub):
    C = priv.C

    columns = C.columns()

    # Randomly shuffle columns
    np.random.seed(2)
    pi = np.random.permutation(len(columns))

    randomized_columns = []
    for i in range(len(columns)):
        sgn = np.random.choice([-1,1])
        col = columns[pi[i]] * sgn
        col = [int(ci) for ci in col]
        randomized_columns += [col]

    # Print the randomized columns to a file
    with open("debug/C.columns", "w") as g:
        for col in randomized_columns:
            g.write(str(col) + "\n")

    # Run the key recovery attack with this file.
    with open("debug/C.columns") as f:
        cols = []
        for line in f:
            col = json.loads(line)
            cols += [col]

    problem = EHTRecoveryFromColumns(pub, cols, verbose=True)
    priv = problem.solve()
    if priv is None:
        return False

    print("Key recovery successful.")
    with open("debug/recovered_private.json", "w") as g:
        g.write(priv)
    
    return True

def main():
    import sys
    fn_sk = sys.argv[1] if len(sys.argv) > 1 else "debug/private.json"
    fn_pk = sys.argv[2] if len(sys.argv) > 2 else "debug/public.json"
    
    priv = load_private(fn_sk)
    pub = load_public(fn_pk)

    assert test_validity(priv, pub)
    assert test_recovery_from_columns(priv, pub)


if __name__ == "__main__":
    main()
