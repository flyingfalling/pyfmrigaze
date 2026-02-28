JOBSDIR=$1
LOGSDIR=$2
ls $JOBSDIR | parallel --jobs 0 "echo RUNNING {} && bash $JOBSDIR/{} &> $LOGSDIR/{}.out"
