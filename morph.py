from sage.all import *
import numpy as np

"""
Given a bunch of vectors C*z (for many unknown vectors z whose coefficients are in {-3, -2, ..., 2, 3}),
compute a transformation L such that C*L should be approximately orthogonal. Output L and the transformed input vectors.

Uses the "Morphing" algorithm from "Learning a Zonotope and More: Cryptanalysis of NTRUSign Countermeasures" by Ducas and Nguyen from Asiacrypt 2012.
https://www.iacr.org/archive/asiacrypt2012/76580428/76580428.pdf
"""

def loadsigs(filename):
	"""
	Load C*z samples from a file produced by 02_process_signatures.sh.
	(If x is the signature of message hash h, then these are (h - A*x) mod 47.)
	"""
	# Input format: each coefficient is a uint8 (taking a value between 0 and 46). 460 bytes per sample.
	sigs = np.fromfile(filename, dtype=np.int8)
	# Here we're reading signed int8 values instead of uint8 values, but that's okay because no entry should be larger than 46.
	nsigs = len(sigs) // 460
	print("number of sigs:",nsigs)
	sigs = (sigs + 23) % 47 - 23 # center around 0
	sigs.resize((nsigs,460))
	# We can run into issues later when computing the covariance matrix due to wraparound mod 47.
	# Each row of C has l1 norm 9, and each z has l_inf norm <= 3.
	# So it's possible a coefficient of Cz could be as high as 27, which mod 47 centered around 0 becomes -20.
	# This will mess up the covariance computation.
	# The solution is to ignore the relatively small number of signatures that have coefficients >= 20 (or <= -20).
	# This ensures no wraparound has happened.
	sigs = np.asfarray([sig for sig in sigs if np.max(np.abs(sig)) <= 19], dtype=np.float64) / 3.
	# We divide by 3 here so that we can pretend coefficients of z were in the range [-1,1] instead of [-3,3].
	return sigs

def covar(vecs):
	""" Compute the covariance matrix of the input """
	return matrix(RDF, np.cov(vecs, rowvar=False, dtype=np.float64))

def morphing(vecs):
	# It's morphing time!
	# Given a bunch of C*z, return L such that L * D_(P(C)) is close to D_(P(C')) where C' is orthogonal
	# i.e., turn a (projection of a) parallelepiped into a (projection of a) hypercube
	# 1. Compute approximation G of C * C.T using covariance
	print(" morphing")
	G = covar(vecs) * 3.
	# 2. Find L such that L * L.T = G^-1
	print("  invert+cholesky")
	L = (~G).cholesky()
	print("  invert+cholesky done")
	# Now L.T * C is close to orthogonal, because
	# (L.T * C).T * (L.T * C) = C.T * (L * L.T) * C = C.T * G^-1 * C
	# ~= C.T * (C * C.T)^-1  * C
	# = C.T * C.T^-1 * C^-1 * C
	# = I
	print(" morphing done")
	return L.T

def preprocess(sigs):
	"""
	Take in a numpy array of sigs (C*z) and morph it. Return the matrix L^-1 and the morphed vectors (as a numpy ndarray)
	"""
	if not isinstance(sigs, np.ndarray):
		print("converting sigs to a numpy array")
		sigs = np.asarray(sigs, dtype=np.float64)
	L = morphing(sigs)
	print(" multiplying by L")
	#sigs =  [L * v for v in sigs]
	sigs = sigs @ L.T
	print(" multiplying by L done")
	Li = ~L
	return Li, sigs

def savestate(filename, Li, vecs):
	assert isinstance(vecs, np.ndarray)
	assert vecs.dtype == np.float64
	np.save(filename + ".Li.npy", np.asarray(Li, dtype=np.float64), allow_pickle=False)
	np.save(filename + ".vecs.npy", vecs, allow_pickle=False)

if __name__ == "__main__":
	from sys import argv
	if len(argv) < 3:
		print(f"Usage: {argv[0]} infile outfile\n  where infile contains the C*z\n  and output will be written to outfile.Li.npy and outfile.vecs.npy")
		exit(1)
	sigs = loadsigs(argv[1])
	Li, sigs = preprocess(sigs)
	savestate(argv[2], Li, sigs)
