## Set up dataframe columns for Taka

#columns=[ "APPA", "FREEFIX", "SUBJ"];


## By frame, by subject, by video, offset to start of FMRI, AP, etc., etc.
## ## t0,


## Select runs of "same side". Problem: may not line up with TR?


## Step 1: find the video and specify its group for each video.

import pandas as pd
import sys
import os

## Assumes single-level layout, e.g. topdir/GRPNAME1/vidname1

def classify_grp_videos_bydir(topdir, vidnamefilt=None):
    mylist=[];
    grpnames=os.listdir(topdir);
    grpnames = [a for a in grpnames if not os.path.isfile(a)];
    for grp in grpnames:
        grppath  = os.path.join(topdir, grp);
        vidnames = os.listdir(grppath);
        for v in vidnames:
            print("[{}]: [{}]".format(grp, v));
            #mylist.append( pd.DataFrame( data=dict( grp=grp, vid=v )) );
            mydf = pd.DataFrame( dict(grp=[grp], vid=[v])  );
            mylist.append( mydf );
            pass;
        pass;
    print(mylist);
    df = pd.concat(mylist);
    print(df);
    return df;

def code_conditions():
    df = pd.DataFrame(
        dict( APPA   =['AP',   'AP',  'PA',   'PA',  '',     '' ],
              FREEFIX=['free', 'fix', 'free', 'fix', 'free', 'fix'],
              grp    =['D',    'F',   'C',    'E'  , 'A',    'B'],
              ispract=['no',   'no',  'no',   'no',  'yes',  'yes'],
              prerest=[15,     15,    15,     15,    3,      3],
             )
        );
    return df;

if __name__=='__main__':
    df = classify_grp_videos_bydir(sys.argv[1]);
    conddf = code_conditions();
    alldf = pd.merge(left=df, right=conddf, on='grp');
    df.to_csv('vidgrps.csv', index=False);
    conddf.to_csv('condgrps.csv', index=False);
    alldf.to_csv('vidcondgrps.csv', index=False);
    pass;
