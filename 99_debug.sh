#!/bin/sh

mkdir -p debug
c_utils/eht_print_sk data/private.sk > debug/private.json
c_utils/eht_print_pk data/public.pk > debug/public.json

python test_attack.py debug/private.json debug/public.json
