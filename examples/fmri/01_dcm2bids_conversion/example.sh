
venv=$1
DICOMDATA=/mnt/coishare/data/szfmri7t/dicomdata
NEWBIDSFOLDER=/mnt/coishare/data/szfmri7t/bids20260213

if [[ ! -d $venv ]]; then
    echo "Specified VENV [$venv] does not exist, please create it (scripts/create_venv.sh)"
else
    source $venv/bin/activate && \
	pip install dcm2bids dcm2niix numpy && \
	bash do_all_szfmri7t_dcm2bids.sh $DICOMDATA $NEWBIDSFOLDER
fi

