


import pandas as pd;
import sys;
import os;
import peyeutils as pu;
from multiprocessing import Pool;
import numpy as np;

def main():
    rowcsv = sys.argv[1]; #REV: this is "all EDFs" (combined with subject info).
    csvdir = sys.argv[2]; #REV: this is just dir.
    
    rowdf = pd.read_csv(rowcsv); #REV: e.g. allfmriedfs.csv
    
    rowdf = rowdf.loc[ (rowdf['haseyetracking'] & (False==rowdf['edferror'])) ];
    
    for i,row in rowdf.iterrows():
        
        mytrials=row['trials_csv'];
        myblocks=row['blocks_csv'];
        mysamples=row['samples_csv'];
        myevents=row['events_csv'];
        subjname=row['name'];
        kind_inout=row['kind'];
        edfdatetime=row['edfdatetime'];
        
        trialdf = pd.read_csv( os.path.join(csvdir, mytrials) );
        blockdf = pd.read_csv( os.path.join(csvdir, myblocks) );
        #samplesdf = pd.read_csv( os.path.join(csvdir, mytrials) );

        print("\n\n S: [{}]   KIND: [{}]  ({})".format(subjname, kind_inout, edfdatetime));
        print("TRIALS:");
        print(trialdf.columns);
        print(trialdf);
        
        print("BLOCKS:");
        print(blockdf);
        
        pass;
    
    #print(rowdf);
    
    exit(0);
    
    #rowdf = rowdf[:5];
    results = list();
    rows=[ dict(row=row,csvdir=csvdir) for i,row in rowdf.iterrows() ];
    
    
    
    
    MULTIPROC=False; #True;
    NPROC=48;
    
    if(MULTIPROC):
        with Pool(processes=NPROC) as pool:
            results = pool.map(process_events, rows);
            pass;
        pass;
    else:
        for rowdict in rows:
            results.append( process_events( rowdict ) );
            pass;
        pass;
    
    rowdf = pd.DataFrame(results);
    print(rowdf);

    for i, row in rowdf.iterrows():
        plotrow(dict(row=row, csvdir=csvdir) );
        pass;
    
    return 0;

if __name__=='__main__':
    exit(main());

