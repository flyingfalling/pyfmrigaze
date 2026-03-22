#!/bin/bash

INDIR=$1   #"/mnt/coishare/data/szfmri7t/SZ_gaze_fmri_BIDS_20251031/"
SUBJ=$2

OUTDIR=$INDIR"/derivatives/fmriprep_persubj/$SUBJ"

WORKDIR="/scratch/SZ_FMRIPREP_WORK/$SUBJ"


#EXTRAOPTS="--fs-no-reconall "
dt="$(date '+%Y-%m-%d-%H-%M-%S')"
EXTRAOPTS=""
EXTRAOPTS+="-w $WORKDIR"
#EXTRAOPTS+=" --low-mem"
EXTRAOPTS+=" --mem-mb 62000"
EXTRAOPTS+=" --nthreads 4"
EXTRAOPTS+=" --omp-nthreads 4"

LOGFILE="/scratch/FMRIPREP_STDOUT_${SUBJ}_${dt}.out"


fmriprep \
    $INDIR \
    $OUTDIR \
    participant \
    --participant-label $SUBJ \
    $EXTRAOPTS \
    --stop-on-first-crash \
    | tee $LOGFILE
