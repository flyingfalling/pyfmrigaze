#!/bin/bash

# FMRIprep installation is complicated.
# It is most commonly recommended to run a "containerized" version of it with all dependencies installed.

## Fmri prep requires:

## fsl
## AFNI
## ANTS
## fmriprep (python lib)
## freesurfer
## C3D
## connectome-workbench
## bids-validator
## nvm
## npm

## Additionally a new binary of "msm" was required on top of an old one.
## msm

## Furthermore, PATH and other linkages must be set so that these can all be found by FMRIPREP when executed.
