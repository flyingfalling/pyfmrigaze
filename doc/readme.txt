FMRI and gaze analysis requires several steps.

FMRI: 
0) Upload the appropriate data (raw dicom data?) to the host (machine/server) filesystem on which it will be processed.

See: examples/00_upload_data

1) Convert DCM data to BIDS format (Taka's scripts modified by richard, calling dcm2bids)
This step requires installing a few packages but basically anyone can run it.
-> Can view dicom data using some data viewers or python libs, but dcm2bids should convert to .tar.gz for the volumes.

See: examples/01_dcm2bids_conversion

OUTPUT: BIDs format data (a specific kind of directory layout and filenaming convention).

2) Run fmriprep preprocessing.
If we add new data, we need to re-run FMRIprep (at least for the new data).
This step (installing FMRIprep so it will run properly) requires many libraries to all work correctly and have system path/settings appropriate. Currently it only is setup on "mazda0" server, possibly only under "rveale" account. Another possibility is to install a containerized version (recommended).
-> registers to templates
-> surface/etc. identification
-> confound (noise)/coregressor identification. (nuisance parameters/motion identification etc.)
-> field distortion correction, etc.

See: examples/02_fmriprep


3) Write script (in my case, python nilearn, but you could also use matlab, FSL etc.) for your analysis. This involes several steps, depending
on the analysis. For the FMRI data, we want to at least read the BIDS format of the type we want (e.g. BOLD data from runs of a certain task),
and summarize what data is available to us (so we can filter some out etc.).

See: examples/03_reading_BIDS_data
