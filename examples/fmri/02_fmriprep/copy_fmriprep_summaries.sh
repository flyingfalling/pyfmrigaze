#!/bin/bash


INDIR=$1
OUTDIR=$2

mkdir -p $OUTDIR

for sdir in `find $1 -maxdepth 1 -type 'd' -name 'sub-*'`; do
    bn=`basename $sdir`
    echo $sdir
    html="$sdir"".html"
    
    if [ -f "$html" ]; then
	echo "Found HTML: ""$html"
    fi
    cp $html $OUTDIR
    #figout="$OUTDIR""/""$bn""/""/figures"
    figout="$OUTDIR""/""$bn"
    mkdir -p $figout
    cp -r "$sdir""/""figures" $figout
done

cp $INDIR/*.tsv $OUTDIR
cp $INDIR/*.json $OUTDIR

#for sdir in `ls $INDIR | grep "sub-"`
