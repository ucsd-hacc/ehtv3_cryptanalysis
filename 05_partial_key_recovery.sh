#!/bin/bash

## Once the columns of C are recovered, we can reconstruct (most of) C, T, and B.
# We don't recover the full private key but we recover enough of it that we can produce signatures by solving CVP in a very low dimension (28 for the category 1 parameters).

# Collect and deduplicate the columns found in step 4 (which may be run on multiple machines)
cat data/descent/*/output_vecs.json | sort | uniq > data/C_vecs.json

python3 partial_key_recovery.py data/public.json data/C_vecs.json data/partial_key.json -v
