This directory contains source code for small C programs that interface
with the EHTv3 reference implementation.

eht_keygen:
	Takes a number 0-99 as input and generates the corresponding key from the KATs.
	Creates a corresponding .pk and .sk file with the raw bytes.

eht_siggen:
	Takes a .sk, number of signatures, and RNG seed as input.
	Prints random signatures to STDOUT, encoded in hex.

eht_sigparse:
	Takes a .pk as a command line argument, and hex-encoded signatures as input.
	Computes vector Cz for each signature and outputs the raw bytes.