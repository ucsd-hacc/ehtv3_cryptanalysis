#!/bin/bash

## Run the first part ("morphing") of the [DucasNguyen12] algorithm for solving the Hidden Zonotope Problem.
# Reads C*z vectors from data/raw_Cz.dat
# Writes transformation matrix L^-1 to data/morphed.Li.npy and transformed vectors to data/morphed.vecs.npy
sage morph.py data/raw_Cz.dat data/morphed
