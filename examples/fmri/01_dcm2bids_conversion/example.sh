
venv=$1
DICOMDATA=/mnt/coishare/data/szfmri7t/SZ_gaze_fmri_dicom_20250530
NEWBIDSFOLDER=/mnt/coishare/data/szfmri7t/bids20260225

#REV: we must ensure we can read each input directory...

if [[ ! -d $venv ]]; then
    echo "Specified VENV [$venv] does not exist, creating... (scripts/create_venv.sh)"
    bash scripts/create_venv.sh $venv
fi

if [[ ! -d $venv ]]; then
    echo "Error: VENV [$venv] does not exist..."
else
    source $venv/bin/activate && \
	pip install dcm2bids dcm2niix numpy && \
	bash do_all_szfmri7t_dcm2bids.sh $DICOMDATA $NEWBIDSFOLDER
fi
