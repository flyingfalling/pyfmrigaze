import pandas as pd
import numpy as np
import sys;
import os;
import peyeutils as pu;

if __name__=='__main__':
    
    alledfs=sys.argv[1];
    csvdir=sys.argv[2];
    
    df = pd.read_csv(alledfs);
    
    cols=list();
    rows=list();

    nogaze=list();
    noedf=list();
    allnans=list();
    for i,row in df.iterrows():
        
        if( False == row['haseyetracking'] ):
            nogaze.append(row);
            pass;
        if( True == row['edferror'] ):
            noedf.append(row);
            pass;
        
        samps = os.path.join(csvdir, row['samples_csv']);
        if( True): #row['haseyetracking'] and not row['edferror'] ):
            df = pd.read_csv(samps);
            if( pu.utils.allnan( df['cgx_dva'] ) ):
                print("[{}] ALL NAN!!!".format(row['edffile']));
                allnans.append(row);
                pass;
            pass;
        
        pass;

    print("No gaze:");
    print([r['edffile'] for r in nogaze]);

    for edf in [r['edffile'] for r in nogaze]:
        myev = os.path.join( csvdir, edf+'.events2.csv' );
        if( os.path.isfile( myev ) ):
            print("EVENTS2 EXISTED!! - {}".format(edf));
            df = pd.read_csv(myev);
            pass;
        else:
            print("EVENTS2 NONE!! - {}".format(edf));
            pass;
        pass;
    
    print("\nNo EDF/error:");
    print([r['edffile'] for r in noedf]);

    print("\nALL NANS:");
    print([r['edffile'] for r in allnans]);
    
    #rowdf.to_csv(alledfs + '_w_events2.csv', index=False);
    exit(0);
    pass;
