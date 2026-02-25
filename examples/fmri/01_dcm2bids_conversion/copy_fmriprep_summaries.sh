#!/bin/bash

#REV: this copies just the HTML files and corresponding figures so that someone can view themwithout copyting the heavy tar.gz data.

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
#for sdir in `ls $INDIR | grep "sub-"`
