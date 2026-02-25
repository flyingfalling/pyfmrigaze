#FREESURFER stuff (need to install locally, /usr/local etc.)
FREESURFER_HOME=/usr/local/freesurfer/7.3.2
export FS_LICENSE=$FREESURFER_HOME/license.txt
source $FREESURFER_HOME/SetUpFreeSurfer.sh

# FSL stuff, note includes PYTHON
#REV: uncomment to let FSL work...                                                                      
FSLDIR=/mnt/coiapps/fsl
APATH=${FSLDIR}
export FSLDIR="$FSLDIR"
export FSL_DIR="$FSLDIR"
. ${FSLDIR}/etc/fslconf/fsl.sh


export PATH=/mnt/coiapps/ants-2.5.4/bin:$PATH
export PATH=/mnt/coiapps/c3d-1.4.2-Linux-gcc64/bin:$PATH

