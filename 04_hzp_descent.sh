#!/bin/bash

## Runs gradient descent to recover columns of C -- this is the second part of the [DucasNguyen12] algorithm.
# Reads from data/morphed.Li.npy and data/morphed.vecs.npy, which are produced by the previous script.
# Writes output vectors to data/descent/output_vecs.json, one vector per line.

INFILE="data/morphed"
OUTDIR="data/descent/`hostname`/" # can be run across multiple machines

NPROCS=$( grep -c ^processor /proc/cpuinfo )
NPROCS=$(( $NPROCS - 1 ))

# Coupon collector problem: to find all 484 distinct vectors, we expect it to take roughly 4400 successful runs of descent
# We'll do 6600 because not every descent run is successful and to make it more likely that we find all 484
# NOTE: update this number if running across multiple machines
ITERSPERJOB=$(( 6600 / $NPROCS + 1 ))

mkdir -p "$OUTDIR"
echo "Launching $NPROCS descent jobs, each doing $ITERSPERJOB runs"
for i in $( seq $NPROCS ); do
	(sage descent.py "$INFILE" "$OUTDIR"/vecs_$i "$ITERSPERJOB" > /dev/null ; echo "Job $i finished" ) &
done
wait
echo "All jobs finished; merging and deduplicating"
cat "$OUTDIR"/vecs_* | sort | uniq > "$OUTDIR"/output_vecs.json
echo "Recovered $( wc -l "$OUTDIR"/output_vecs.json ) distinct vectors"
