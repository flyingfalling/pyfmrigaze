#!/bin/bash

## THIS WILL NOT WAIT.
logdir='logs';
mkdir -p $logdir
for script in `ls ./jobs`;
do
    outf=$logdir"/"`basename "$script"`".out"
    echo "EXECUTING $script (output to ""$outf"")"
    bash "./jobs/"$script &> $outf &
done
