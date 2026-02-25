#!/bin/bash
#fmriprep --stop-on-first-crash /mnt/coishare/data/szfmri7t/SZ_gaze_fmri_BIDS_20250530/ /mnt/coishare/data/szfmri7t/SZ_gaze_fmri_BIDS_20250530/derivatives/fmriprep participant -w /scratch/SZ_FMRIPREP_WORKSPACE

#REV: NOTE https://www.youtube.com/watch?v=4W6qBIpE404  (fmriprep walkthrough).

INDIR=$1   #"/mnt/coishare/data/szfmri7t/SZ_gaze_fmri_BIDS_20251031/"
OUTDIR=$INDIR"/derivatives/fmriprep"

WORKDIR="/scratch/SZ_FMRIPREP_WORKSPACE"

#nthreads=16

#EXTRAOPTS="--fs-no-reconall --nthreads $nthreads"
dt="$(date '+%Y-%m-%d-%H-%M-%S')"
EXTRAOPTS="" #-w $WORKDIR

LOGFILE="/scratch/FMRIPREP_STDOUT_${dt}.out"

echo "Tee-ing to [$LOGFILE]"




fmriprep \
    $INDIR \
    $OUTDIR \
    participant \
    $EXTRAOPTS \
    | tee $LOGFILE
