## Your data is in a directory (folder) whose absolute path is $LOCALPATH
## Example: /home/riveale/fmri_dcm_data.
## (inside fmri_dcm_data there is folders:
# patient01, patient02, control01, control02, etc.

## You will upload to USER@REMOTEHOST:$REMOTEPATH
## It will create the directory (if it does not exist $REOMTEPATH/fmri_dcm_data)

## Make sure $LOCALPATH **does not** have a trailing / (i.e. NOT fmri_dcm_data/)
## Make sure $REMOTEPATH **does** have a trailing /
# Otherwise it will copy the contents of $LOCALPATH to remotepath (i.e. control01, patient01 will be in $REMOTEPATH directly).

## You can also use --progress= or other options.
rsync -avzt $LOCALPATH $USER@$REMOTEHOST:$REMOTEPATH
