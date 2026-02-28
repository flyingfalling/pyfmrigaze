DCMDIR=$1

find $DCMDIR -maxdepth 1 -type 'd' -name "C*" -exec basename {} \;
find $DCMDIR -maxdepth 1 -type 'd' -name "P*" -exec basename {} \;
