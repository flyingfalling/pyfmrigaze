#python3 -m venv dcm2bids_venv
#pip install dcm2bids dcm2niix
#source dcm2bids_venv/bin/activate

SCRIPTS="./scripts"

DATADIR='/mnt/coishare/data/szfmri7t/'
ORIG_DICOM_DIR=$1   # "$DATADIR"'/SZ_gaze_fmri_dicom_20250530/'
NEW_BIDS_DIR=$2     # "$DATADIR"'/SZ_gaze_fmri_BIDS_20251031'

LOGSDIR="/tmp/dcm2bids_logs"
mkdir -p $LOGSDIR

JOBSDIR="/tmp/dcm2bids_jobs"


#Make sure ORIG_DICOM_DIR has *ONLY participants (C302, P920) dirs, and inside those, only the extracted directories given to us by the FMRI people (20230703_1209_MM_054Y_M etc.)

## if the tar.gz etc. are still there, I will error it out. Those should be deleted/cleaned different way (see the tree/search/find and delete, and extract script elsewhere).

##   >>>>> 0) Create an empty template (scaffold):
dcm2bids_scaffold -o $NEW_BIDS_DIR



##   >>>>>  1) Create/copy subjects index. There are two:

## a) age/sex/id/group
# THis is from orig dicom data
#Note it is organized as:
## DIR/C301/BLAH_BLAH_BLAH/*
## Where BLAH_BLAH_BLAH is the directory name given by the 7T MRI people, which includes
## initials, date, time, sex, age

##    Extracts if via the BLAH_BLAH_BLAH above
python $SCRIPTS/create_name_age_sex_index.py $ORIG_DICOM_DIR
cp name_age_sex_index.csv "$NEW_BIDS_DIR"'/participants.tsv'


##   >>>>>  2) Create scripts that run the dcm2bids (and some other helper scripts) to do the
##     actual conversion

## Note must modify some directories and filenames in here (and in the python script too if there are
## assumptions about dir layout).
LIST_OF_SUBJS='subj_list_sz.txt'

bash $SCRIPTS/cat_subj_list.sh $ORIG_DICOM_DIR > $LIST_OF_SUBJS

## This will create *.sh files in ./jobs
bash $SCRIPTS/create_job_dcm2bids.sh $LIST_OF_SUBJS $JOBSDIR $ORIG_DICOM_DIR $NEW_BIDS_DIR



echo "Running in parallel DCM2BIDS, logs in ${LOGSDIR}"

## Run jobs
bash $SCRIPTS/parallel_run_all.sh $JOBSDIR $LOGSDIR
