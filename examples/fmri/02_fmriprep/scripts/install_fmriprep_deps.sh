#!/bin/bash
MYVENV=~/venvs/fmriprepvenv
python3 -m venv $MYVENV
source $MYVENV/bin/activate

#FSL
#https://fsl.fmrib.ox.ac.uk/fsl/docs/
wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslconda/releases/fslinstaller.py

python fslinstaller.py

#specify /mnt/coiapps/fsl

#ANTS
#https://github.com/ANTsX/ANTs
wget https://github.com/ANTsX/ANTs/releases/download/v2.5.4/ants-2.5.4-ubuntu-22.04-X64-gcc.zip

unzip ants-2.5.4-ubuntu-22.04-X64-gcc.zip
mv ants-2.5.4 /mnt/coiapps

#in .profile
export PATH=/mnt/coiapps/ants-2.5.4/bin:$PATH


# AFNI https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/background_install/install_instructs/steps_linux_ubuntu22.html
# Note removed firefox, evince, etc. from install in first script.

#c3D
wget https://sourceforge.net/projects/c3d/files/c3d/Nightly/c3d-nightly-Linux-gcc64.tar.gz

tar xfz c3d-nightly-Linux-gcc64.tar.gz

#https://sourceforge.net/p/c3d/git/ci/master/tree/doc/c3d.md
mv c3d-1.4.2-Linux-gcc64 /mnt/coiapps

## add /mnt/coiapps/c3d-1.4.2-Linux-gcc64/bin to $PATH in .profile


## FREESURFER

# https://surfer.nmr.mgh.harvard.edu/fswiki//FS7_linux
#https://surfer.nmr.mgh.harvard.edu/fswiki/rel7downloads
## note version 8 is available...used 7

wget https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.4.0/freesurfer_ubuntu22-7.4.0_amd64.deb

sudo apt install ./freesurfer_ubuntu22-7.4.0_amd64.deb



## bids-validator
# Installed deno (a javascript runtime?)
#curl -fsSL https://deno.land/install.sh | sh
#

## No, should do via NPM? https://www.npmjs.com/package/bids-validator

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash

source ~/.bashrc
nvm list-remote
nvm install v22.14.0
#npm install --global npm@^7   # REV: @^7 implies version 7 ...
npm install --global npm@^7

npm install -g bids-validator


## Connectome workbench
#Instructions at :
http://neuro.debian.net/install_pkg.html?p=connectome-workbench

wget -O- http://neuro.debian.net/lists/jammy.us-ca.full | sudo tee /etc/apt/sources.list.d/neurodebian.sources.list

sudo apt-key adv --recv-keys --keyserver hkps://keyserver.ubuntu.com 0xA5D32F012649A5A9

sudo apt-get update
sudo apt-get install connectome-workbench




#REV: error in surface.py, had to get git and install from there. (_midthickness_wf)
##pip install fmriprep
