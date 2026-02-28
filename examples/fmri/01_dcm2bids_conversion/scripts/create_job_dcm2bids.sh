#!/bin/bash

SCRIPTS=./scripts

Configfile="./BIDS_config_templates/config_dcm2bids_FIXED_FMAP.json"
DataList=$1  #just list of subjects, probably just ls showing P001, P002, C330, etc.
JOBSDIR=$2

DicomFolder=$3
TARGETDIR=$4

mkdir -p ${JOBSDIR}

echo "JOB data stored in [${JOBSDIR}]"

cat $DataList | while read Subject;
do
    subnum=$Subject #REV: fixed...since Taka organized nicely into CXXX and SXXX
    
    SubjectDataFolder=${DicomFolder}/${Subject}
    SUBJ_SCRIPT="${JOBSDIR}""/""${subnum}""_dcm2bids.sh"
    echo "Creating script ${SUBJ_SCRIPT} for subject ${subnum}"
    echo "echo \"Doing for subject: [$subnum]\"" > $SUBJ_SCRIPT
    
    echo "dcm2bids -d ${SubjectDataFolder} -p $subnum -c ${Configfile} -o ${TARGETDIR}" >> $SUBJ_SCRIPT
    
    echo "python $SCRIPTS/remove_bidsuri.py $subnum $TARGETDIR" >> $SUBJ_SCRIPT
done
