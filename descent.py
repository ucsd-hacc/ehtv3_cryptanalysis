from sage.all import *
import numpy as np

"""
Implements the gradient descent part of the SolveHZP algorithm from
"Learning a Zonotope and More: Cryptanalysis of NTRUSign Countermeasures" by Ducas and Nguyen from Asiacrypt 2012.
https://www.iacr.org/archive/asiacrypt2012/76580428/76580428.pdf
"""
def loadstate(filename):
	Li = matrix(RDF, np.load(filename + ".Li.npy", allow_pickle=False))
	vecs = np.lib.format.open_memmap(filename + ".vecs.npy", mode='r')
	return Li, vecs

# Calculate 4th moment and gradient of 4th moment
def mom4_and_grmom4(z, vecs):
	assert isinstance(vecs, np.ndarray)
	z = np.asarray(z, dtype=np.float64)
	tmp = vecs @ z
	mom4 = np.mean(tmp**4)
	grmom4 = ((4 * tmp**3) @ vecs) / len(vecs)
	return float(mom4), vector(RDF, grmom4)

def _descent_helper(vecs, w_init, delta=0.7):
	# Find a minimum of the function
	# mom4(w) := E_{x from vecs} [ <x, w>^4 ]
	# via gradient descent starting from w_init
	# (Algorithm 2)
	print("descent start")
	w = w_init
	m, gm = mom4_and_grmom4(w, vecs)
	while True:
		print("descending", m)
		wnew = w - delta * gm
		wnew = wnew / wnew.norm()
		mnew, gm = mom4_and_grmom4(wnew, vecs)
		#if mnew >= m:
		if m - mnew < .00001: # at some point we say "close enough"
			print("descent finished")
			return w, m
		w,m = wnew,mnew

def descent_loop(filename, delta=0.7, iters=1):
	Li, vecs = loadstate(filename)
	# Note: for descent, we want very fast mom4/gradmom4 computation (because we do it many times)
	# So we load all the signatures into RAM instead of using a memory-mapped file.
	n = len(vecs[0])
	for i in range(iters):
		w = vector([gauss(0,1) for _ in range(n)])
		w = w / w.norm()
		r, m = _descent_helper(vecs, w, delta)
		if m < 1/3:
			gamma = sqrt(sqrt(((1/3 - m)*15/2))) # scale
		else:
			gamma = 1
		out = gamma * Li * r
		out = vector([int(round(t)) for t in out])
		if out < -out:
			out = -out # makes deduplication easier
		yield out

def descent_oneshot(filename, delta=0.7):
	return next(descent_loop(filename, delta, iters=1))

if __name__ == "__main__":
	from sys import argv
	if len(argv) not in (3,4):
		print(f"Usage: {argv[0]} infilename outfilename [loopcount]")
		exit(1)
	if len(argv) == 4:
		iters = int(argv[3])
		with open(argv[2], 'w') as f:
			vs = descent_loop(argv[1], delta=0.7, iters=iters)
			for v in vs:
				if v != 0:
					f.write("[" + ", ".join("%d" % vi for vi in v) + "]\n")
					f.flush()
	else:
		v = descent_oneshot(argv[1], delta=0.7)
		if v == 0:
			print("recovered vector is obviously wrong :(")
			exit()
		print(f"Found a vector with l1 norm {v.norm(1)}!")
		with open(argv[2], 'w') as f:
			f.write("[" + ", ".join("%d" % vi for vi in v) + "]\n")
