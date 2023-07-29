#!/bin/bash

## Using the partial private key, forge a signature of an arbitrary message
MESSAGE='Forgery!'
python3 fake_sign.py data/partial_key.json "$MESSAGE" > data/forged_signature.sig
echo "Forged signature is in data/forged_signature.sig"
./c_utils/eht_verify data/public.pk <data/forged_signature.sig
