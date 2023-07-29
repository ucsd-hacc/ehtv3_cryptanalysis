#!/bin/bash

processCz_task(){
    f=$1
    echo $f
    cat $f | ./c_utils/eht_sigparse data/public.pk > $f.raw_Cz.dat
}

# Process the signatures using the public key to get a numpy array file with Cz values

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
for f in `ls data/SIGS*`; do
    run_with_lock processCz_task $f
done
wait

cat data/*.raw_Cz.dat > data/raw_Cz.dat
