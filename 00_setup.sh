#!/bin/sh

KEYID=0
make -C c_utils
mkdir -p data
./c_utils/eht_keygen $KEYID
mv private.sk data/ # used only for signature generation
mv public.pk data/
./c_utils/eht_print_pk data/public.pk > data/public.json
