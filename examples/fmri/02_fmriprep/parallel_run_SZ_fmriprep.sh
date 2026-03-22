#!/bin/bash
#fmriprep --stop-on-first-crash /mnt/coishare/data/szfmri7t/SZ_gaze_fmri_BIDS_20250530/ /mnt/coishare/data/szfmri7t/SZ_gaze_fmri_BIDS_20250530/derivatives/fmriprep participant -w /scratch/SZ_FMRIPREP_WORKSPACE

#REV: NOTE https://www.youtube.com/watch?v=4W6qBIpE404  (fmriprep walkthrough).

INDIR=$1   #"/mnt/coishare/data/szfmri7t/SZ_gaze_fmri_BIDS_20251031/"
SUBJFILE=/tmp/subjID.txt

WORKDIR=/scratch/SZ_FMRIPREP_WORK
mkdir -p $WORKDIR

ls -d $INDIR/sub-* | cut -d'-' -f2 > $SUBJFILE

#SUBJS=$(ls -d $INDIR/sub-* | cut -d'-' -f2)

#echo $SUBJS

NJOBS=6

cat $SUBJFILE | parallel -j $NJOBS \
			 "./single_subj_SZ_fmriprep.sh $INDIR {}"
