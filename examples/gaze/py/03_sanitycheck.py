import pandas as pd
import numpy as np
import sys;
import os;
import peyeutils as pu;

if __name__=='__main__':
    
    alledfs=sys.argv[1];
    csvdir=sys.argv[2];
    
    df = pd.read_csv(alledfs);
    
    rows=list();
    for i,row in df.iterrows():
        
        hasgaze=row['haseyetracking'];
        
        
        mytrials=row['trials_csv'];
        myblocks=row['blocks_csv'];
        mysamples=row['samples_csv'];
        myevents=row['events2_csv'];
        origedf=row['edffile'];
        
        
        subjname=row['name'];
        kind_inout=row['kind'];
        edfdatetime=row['edfdatetime'];
        
        trialdf = pd.read_csv( os.path.join(csvdir, mytrials) );
        blockdf = pd.read_csv( os.path.join(csvdir, myblocks) );
        
        
        #mysamps=row['samples_csv'];
        #samppath=os.path.join(csvdir, mysamps);
        #sdf = pd.read_csv(samppath);
        #if( not os.path.isfile(samppath) ):
        #    raise Exception("Expected samples missing [{}]".format(samppath));

        ntrials = len(trialdf.index);
        nblocks = len(blockdf.index);
        print("\n\n S: [{}]   KIND: [{}]  ({})".format(subjname, kind_inout, edfdatetime));
        print("[{}]  [{}] trials   in [{}] blocks".format(origedf, ntrials, nblocks));
        
        if( False == hasgaze ):
            print("Skipping (no gaze)");
            continue;

        sdf = pd.read_csv( os.path.join(csvdir, mysamples) );
        edf = pd.read_csv( os.path.join(csvdir, myevents ) );
        
        lensec=sdf['Tsec'].max() - sdf['Tsec'].min();

        nleye_samps = len(sdf[ sdf.eye == 'L' ].index);
        nreye_samps = len(sdf[ sdf.eye == 'R' ].index);
        nbeye_samps = len(sdf[ sdf.eye == 'B' ].index);

        nleye_notna = sdf[ sdf.eye == 'L' ].cgx_dva.count();
        nreye_notna = sdf[ sdf.eye == 'R' ].cgx_dva.count();
        nbeye_notna = sdf[ sdf.eye == 'B' ].cgx_dva.count();

        nleye_notbad = len( sdf[ (sdf.eye == 'L') & (sdf.bad == False) ].index );
        nreye_notbad = len( sdf[ (sdf.eye == 'R') & (sdf.bad == False) ].index );
        nbeye_notbad = len( sdf[ (sdf.eye == 'B') & (sdf.bad == False) ].index );

        nlsaccs = len(edf[ (edf.eye == 'L') & (edf.label == 'SACC') ].index);
        nrsaccs = len(edf[ (edf.eye == 'R') & (edf.label == 'SACC') ].index);
        nbsaccs = len(edf[ (edf.eye == 'B') & (edf.label == 'SACC') ].index);

        nl_bsaccs = len(edf[ (edf.eye == 'L') & (edf.label == 'SACCBLNK') ].index);
        nr_bsaccs = len(edf[ (edf.eye == 'R') & (edf.label == 'SACCBLNK') ].index);
        nb_bsaccs = len(edf[ (edf.eye == 'B') & (edf.label == 'SACCBLNK') ].index);

        print("LEFT: {:6d}/{:6d} ({:4.1f}%) GOOD   ({:6d} FINITE) ({:4.1f}%)".format(nleye_notbad, nleye_samps, 100*nleye_notbad/nleye_samps, nleye_notna, 100*nleye_notna/nleye_samps));
        print("RGHT: {:6d}/{:6d} ({:4.1f}%) GOOD   ({:6d} FINITE) ({:4.1f}%)".format(nreye_notbad, nreye_samps, 100*nreye_notbad/nreye_samps, nreye_notna, 100*nreye_notna/nreye_samps));
        print("BINO: {:6d}/{:6d} ({:4.1f}%) GOOD   ({:6d} FINITE) ({:4.1f}%)".format(nbeye_notbad, nbeye_samps, 100*nbeye_notbad/nbeye_samps, nbeye_notna, 100*nbeye_notna/nbeye_samps));
        #print("RGHT: {:6d}/{:6d} ");
        #print("BINO: {:6d}/{:6d} ");
        
        pass;
    
    exit(0);
    pass;
