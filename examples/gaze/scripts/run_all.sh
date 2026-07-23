#!/bin/bash

#/scratch/fmri7tcsvs/

SAMPCSVDIR=${1:-./fmri7t_csvs}

echo "CSVs will be in: ${SAMPCSVDIR}"


### Laptop
#FREEVIEWINGDATADIR='/home/riveale/richard_home/git/freeviewingsvn/'
#PATIENTIDXDIR='/home/riveale/data/schizo_outofscanner_fromtaka/patient_info/'
#VIDCLIPDIR='/home/riveale/Desktop/stimuli/fmri_lab90c2/'

### COI cluster
FREEVIEWINGDATADIR='/mnt/coishare/data/freeviewing/'
PATIENTIDXDIR='/mnt/coishare/data/szfmri7t/data/patient_info/'
VIDCLIPDIR='/mnt/coishare/data/stimuli/fmri_lab90c2/'


SZIDX='/20260307/統合失調症患者_7期_心理検査データ_20260307.xlsx'
HCIDX='/20260307/健常者_7期_心理検査データ_20260307.xlsx'


### CSV NAMES
CONDCSV="vidcondgrps.csv"

EDFIDX="sz_edf_index.csv"
BLOCKIDX="allfmriblocks.csv"
TRIALIDX="allfmritrials.csv"

EDFIDX2="allfmriedfs.csv"




mkdir -p ${SAMPCSVDIR}

### CONSTRUCT FILE PATHS
FMRIEDFDIR="${FREEVIEWINGDATADIR}/data/fmri7t"
OUTSIDEEDFDIR="${FREEVIEWINGDATADIR}/data/fmri7t_outside_sorted/"


## Just makes video groups
python py/00_classify_vid_groups.py $VIDCLIPDIR

## Computes index from subject data and EDF dir etc.
## Index here means list of subjects etc.?
python py/00_parse_SZ_index.py ${PATIENTIDXDIR}/${SZIDX} ${PATIENTIDXDIR}/${HCIDX} ${FMRIEDFDIR} ${OUTSIDEEDFDIR}


## Extracts trials etc. (multithreaded)
## REV: produces MASSIVE data CSVs...
python py/01_extract_SZ_edfs.py ${EDFIDX} ${FMRIEDFDIR} ${OUTSIDEEDFDIR} ${SAMPCSVDIR}


