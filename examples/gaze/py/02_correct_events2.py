

import pandas as pd
import numpy as np
import sys;
import os;

if __name__=='__main__':

    alledfs=sys.argv[1];
    csvdir=sys.argv[2];

    df = pd.read_csv(alledfs);

    if( 'events2_csv' in df.columns ):
        raise Exception("Good exception, events2 already exists...");
    missing=list();
    missingname=list();
    noeye=list();
    rows=list();
    for i,row in df.iterrows():
        mysamps=row['samples_csv'];
        events2_csv = mysamps.removesuffix('.samples.csv') + '.events2.csv';
        path=os.path.join(csvdir, events2_csv);
        if( False == row['haseyetracking']):
            noeye.append(path);
            print("Skipping [{}] (no eyetracking, i.e. all NAN)".format(path));
            events2_csv='';
            continue;

        row['events2_csv'] = events2_csv;
        
        if( os.path.isfile( path ) ):
            rows.append(row);
            print("SUCCESS: [{}]".format(path));
            pass;
        else:
            #raise Exception("Missing expected [{}]".format(path));
            print("Missing expected [{}]".format(path));
            missing.append(path);
            missingname.append(events2_csv);
            pass;
                
        pass;
    
    print("Missing:");
    print(missing);
    
    if( len(missing) > 0 ):
        raise Exception("Failure, missing some!");
    
    #rowdf = pd.concat(rows);
    rowdf = pd.DataFrame(rows);
    print(rowdf);
    
    rowdf.to_csv(alledfs + '.w_events2.csv', index=False);
    exit(0);
    pass;
