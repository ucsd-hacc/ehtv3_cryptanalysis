#!/bin/bash

# Do parallelized signature generation
NSIGS=500000
BATCHSIZE=10000

NBATCHES=$(( $NSIGS / $BATCHSIZE ))

# Parallelize signature generation
siggen_task(){
    FNAME="data/SIGS_${BATCHSIZE}_${1}"
    echo $FNAME
   ./c_utils/eht_siggen data/private.sk $BATCHSIZE $1 > $FNAME
}

# Number of threads to use
NT=`grep -c ^processor /proc/cpuinfo`
NT=$(( $NT - 1 ))

# https://unix.stackexchange.com/questions/103920/parallelize-a-bash-for-loop
# initialize a semaphore with a given number of tokens
open_sem(){
    mkfifo pipe-$$
    exec 3<>pipe-$$
    rm pipe-$$
    local i=$1
    for((;i>0;i--)); do
        printf %s 000 >&3
    done
}

# run the given command asynchronously and pop/push tokens
run_with_lock(){
    local x
    # this read waits until there is something to read
    read -u 3 -n 3 x && ((0==x)) || exit $x
    (
     ( "$@"; )
    # push the return code of the command to the semaphore
    printf '%.3d' $? >&3
    )&
}

open_sem $NT
for thing in `seq 1 $NBATCHES`; do
    run_with_lock siggen_task $thing
done
wait
