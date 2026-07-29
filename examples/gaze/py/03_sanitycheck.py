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
        edferr=row['edferror'];
        
        
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
        
        if( (False == hasgaze) or (True == edferr ) ):
            print("Skipping (no gaze)");
            continue;

        sdf = pd.read_csv( os.path.join(csvdir, mysamples) );
        edf = pd.read_csv( os.path.join(csvdir, myevents ) );
        
        lensec=sdf['Tsec'].max() - sdf['Tsec'].min();

        #print(edf[edf.eye=='R']);
        
        
        nleye_samps = len(sdf[ sdf.eye == 'L' ].index);
        nreye_samps = len(sdf[ sdf.eye == 'R' ].index);
        nbeye_samps = len(sdf[ sdf.eye == 'B' ].index);
        
        dt = lensec / nleye_samps;
        
        
        nleye_notna = sdf[ sdf.eye == 'L' ].cgx_dva.count();
        nreye_notna = sdf[ sdf.eye == 'R' ].cgx_dva.count();
        nbeye_notna = sdf[ sdf.eye == 'B' ].cgx_dva.count();
        
        nlpupil_notna = sdf[ sdf.eye == 'L' ].pa.count();
        nrpupil_notna = sdf[ sdf.eye == 'R' ].pa.count();
        nbpupil_notna = sdf[ sdf.eye == 'B' ].pa.count();

        nleye_notbad = len( sdf[ (sdf.eye == 'L') & (sdf.bad == False) ].index );
        nreye_notbad = len( sdf[ (sdf.eye == 'R') & (sdf.bad == False) ].index );
        nbeye_notbad = len( sdf[ (sdf.eye == 'B') & (sdf.bad == False) ].index );
        
        
        print("LEFT: {:6d}/{:6d} ({:4.1f}%) GOOD   ({:6d} FINITE) ({:4.1f}%) (Pupl: {:6d})".format(nleye_notbad, nleye_samps, 100*nleye_notbad/nleye_samps, nleye_notna, 100*nleye_notna/nleye_samps, nlpupil_notna));
        print("RGHT: {:6d}/{:6d} ({:4.1f}%) GOOD   ({:6d} FINITE) ({:4.1f}%) (Pupl: {:6d})".format(nreye_notbad, nreye_samps, 100*nreye_notbad/nreye_samps, nreye_notna, 100*nreye_notna/nreye_samps, nrpupil_notna));
        print("BINO: {:6d}/{:6d} ({:4.1f}%) GOOD   ({:6d} FINITE) ({:4.1f}%) (Pupl: {:6d})".format(nbeye_notbad, nbeye_samps, 100*nbeye_notbad/nbeye_samps, nbeye_notna, 100*nbeye_notna/nbeye_samps, nbpupil_notna));
        #print("RGHT: {:6d}/{:6d} ");
        #print("BINO: {:6d}/{:6d} ");


        nlsaccs = len(edf[ (edf.eye == 'L') & (edf.label == 'SACC') ].index);
        nrsaccs = len(edf[ (edf.eye == 'R') & (edf.label == 'SACC') ].index);
        nbsaccs = len(edf[ (edf.eye == 'B') & (edf.label == 'SACC') ].index);
        
        minlsaccs = edf[ (edf.eye == 'L') & (edf.label == 'SACC') ].dursec.min();
        minrsaccs = edf[ (edf.eye == 'R') & (edf.label == 'SACC') ].dursec.min();
        minbsaccs = edf[ (edf.eye == 'B') & (edf.label == 'SACC') ].dursec.min();
        
        maxlsaccs = edf[ (edf.eye == 'L') & (edf.label == 'SACC') ].dursec.max();
        maxrsaccs = edf[ (edf.eye == 'R') & (edf.label == 'SACC') ].dursec.max();
        maxbsaccs = edf[ (edf.eye == 'B') & (edf.label == 'SACC') ].dursec.max();
        
        medlsaccs = edf[ (edf.eye == 'L') & (edf.label == 'SACC') ].dursec.median();
        medrsaccs = edf[ (edf.eye == 'R') & (edf.label == 'SACC') ].dursec.median();
        medbsaccs = edf[ (edf.eye == 'B') & (edf.label == 'SACC') ].dursec.median();
        
        print("SACCS:");
        if( nlsaccs > 1 ):
            print("  LEFT: {:4d} saccs / {:4.1f} secs ({:2.1f}/sec). DUR: {:4.1f} ({:4.1f}-{:4.1f})".format(nlsaccs, dt*nleye_notna, nlsaccs/(nleye_notna*dt), 1e3*medlsaccs, 1e3*minlsaccs, 1e3*maxlsaccs) );
            pass;
        if(nrsaccs > 1 ):
            print("  RGHT: {:4d} saccs / {:4.1f} secs ({:2.1f}/sec). DUR: {:4.1f} ({:4.1f}-{:4.1f})".format(nrsaccs, dt*nreye_notna, nrsaccs/(nreye_notna*dt), 1e3*medrsaccs, 1e3*minrsaccs, 1e3*maxrsaccs) );
            pass;
        if(nbsaccs > 1 ):
            print("  BINO: {:4d} saccs / {:4.1f} secs ({:2.1f}/sec). DUR: {:4.1f} ({:4.1f}-{:4.1f})".format(nbsaccs, dt*nbeye_notna, nbsaccs/(nbeye_notna*dt), 1e3*medbsaccs, 1e3*minbsaccs, 1e3*maxbsaccs) );
            pass;
        
        
        nlsaccblnks = len(edf[ (edf.eye == 'L') & (edf.label == 'SACCBLNK') ].index);
        nrsaccblnks = len(edf[ (edf.eye == 'R') & (edf.label == 'SACCBLNK') ].index);
        nbsaccblnks = len(edf[ (edf.eye == 'B') & (edf.label == 'SACCBLNK') ].index);
        
        minlsaccblnks = edf[ (edf.eye == 'L') & (edf.label == 'SACCBLNK') ].dursec.min();
        minrsaccblnks = edf[ (edf.eye == 'R') & (edf.label == 'SACCBLNK') ].dursec.min();
        minbsaccblnks = edf[ (edf.eye == 'B') & (edf.label == 'SACCBLNK') ].dursec.min();
        
        maxlsaccblnks = edf[ (edf.eye == 'L') & (edf.label == 'SACCBLNK') ].dursec.max();
        maxrsaccblnks = edf[ (edf.eye == 'R') & (edf.label == 'SACCBLNK') ].dursec.max();
        maxbsaccblnks = edf[ (edf.eye == 'B') & (edf.label == 'SACCBLNK') ].dursec.max();
        
        medlsaccblnks = edf[ (edf.eye == 'L') & (edf.label == 'SACCBLNK') ].dursec.median();
        medrsaccblnks = edf[ (edf.eye == 'R') & (edf.label == 'SACCBLNK') ].dursec.median();
        medbsaccblnks = edf[ (edf.eye == 'B') & (edf.label == 'SACCBLNK') ].dursec.median();
        
        print("SACC/BLNKS:");
        if(nlsaccblnks > 1 ):
            print("  LEFT: {:4d} saccs / {:4.1f} secs ({:2.1f}/sec). DUR: {:4.1f} ({:4.1f}-{:4.1f})".format(nlsaccblnks, dt*nleye_notna, nlsaccblnks/(nleye_notna*dt), 1e3*medlsaccblnks, 1e3*minlsaccblnks, 1e3*maxlsaccblnks) );
            pass;
        if(nrsaccblnks > 1 ):
            print("  RGHT: {:4d} saccs / {:4.1f} secs ({:2.1f}/sec). DUR: {:4.1f} ({:4.1f}-{:4.1f})".format(nrsaccblnks, dt*nreye_notna, nrsaccblnks/(nreye_notna*dt), 1e3*medrsaccblnks, 1e3*minrsaccblnks, 1e3*maxrsaccblnks) );
            pass;
        if(nbsaccblnks > 1 ):
            print("  BINO: {:4d} saccs / {:4.1f} secs ({:2.1f}/sec). DUR: {:4.1f} ({:4.1f}-{:4.1f})".format(nbsaccblnks, dt*nbeye_notna, nbsaccblnks/(nbeye_notna*dt), 1e3*medbsaccblnks, 1e3*minbsaccblnks, 1e3*maxbsaccblnks) );
            pass;
        
        
        #REV: ISIs "stop" at loss of data...right? Or do we "smooth" over some small missing?
        nlisis = len(edf[ (edf.eye == 'L') & (edf.label == 'ISI') ].index);
        nrisis = len(edf[ (edf.eye == 'R') & (edf.label == 'ISI') ].index);
        nbisis = len(edf[ (edf.eye == 'B') & (edf.label == 'ISI') ].index);

        minlisis = edf[ (edf.eye == 'L') & (edf.label == 'ISI') ].dursec.min();
        minrisis = edf[ (edf.eye == 'R') & (edf.label == 'ISI') ].dursec.min();
        minbisis = edf[ (edf.eye == 'B') & (edf.label == 'ISI') ].dursec.min();
        
        maxlisis = edf[ (edf.eye == 'L') & (edf.label == 'ISI') ].dursec.max();
        maxrisis = edf[ (edf.eye == 'R') & (edf.label == 'ISI') ].dursec.max();
        maxbisis = edf[ (edf.eye == 'B') & (edf.label == 'ISI') ].dursec.max();
        
        medlisis = edf[ (edf.eye == 'L') & (edf.label == 'ISI') ].dursec.median();
        medrisis = edf[ (edf.eye == 'R') & (edf.label == 'ISI') ].dursec.median();
        medbisis = edf[ (edf.eye == 'B') & (edf.label == 'ISI') ].dursec.median();

        print("ISIS:");
        if(nlisis > 1 ):
            print("  LEFT: {:4d} isis / {:4.1f} secs ({:2.1f}/sec). DUR: {:4.1f} ({:4.1f}-{:4.1f})".format(nlisis, dt*nleye_notna, nlisis/(nleye_notna*dt), 1e3*medlisis, 1e3*minlisis, 1e3*maxlisis) );
            pass;
        if(nrisis > 1 ):
            print("  RGHT: {:4d} isis / {:4.1f} secs ({:2.1f}/sec). DUR: {:4.1f} ({:4.1f}-{:4.1f})".format(nrisis, dt*nreye_notna, nrisis/(nreye_notna*dt), 1e3*medrisis, 1e3*minrisis, 1e3*maxrisis) );
            pass;
        if(nbisis > 1 ):
            print("  BINO: {:4d} isis / {:4.1f} secs ({:2.1f}/sec). DUR: {:4.1f} ({:4.1f}-{:4.1f})".format(nbisis, dt*nbeye_notna, nbisis/(nbeye_notna*dt), 1e3*medbisis, 1e3*minbisis, 1e3*maxbisis) );
            pass;




        #REV: Blnks "stop" at loss of data...right? Or do we "smooth" over some small missing?
        nlblnks = len(edf[ (edf.eye == 'L') & (edf.label == 'BLNK') ].index);
        nrblnks = len(edf[ (edf.eye == 'R') & (edf.label == 'BLNK') ].index);
        nbblnks = len(edf[ (edf.eye == 'B') & (edf.label == 'BLNK') ].index);

        minlblnks = edf[ (edf.eye == 'L') & (edf.label == 'BLNK') ].dursec.min();
        minrblnks = edf[ (edf.eye == 'R') & (edf.label == 'BLNK') ].dursec.min();
        minbblnks = edf[ (edf.eye == 'B') & (edf.label == 'BLNK') ].dursec.min();
        
        maxlblnks = edf[ (edf.eye == 'L') & (edf.label == 'BLNK') ].dursec.max();
        maxrblnks = edf[ (edf.eye == 'R') & (edf.label == 'BLNK') ].dursec.max();
        maxbblnks = edf[ (edf.eye == 'B') & (edf.label == 'BLNK') ].dursec.max();
        
        medlblnks = edf[ (edf.eye == 'L') & (edf.label == 'BLNK') ].dursec.median();
        medrblnks = edf[ (edf.eye == 'R') & (edf.label == 'BLNK') ].dursec.median();
        medbblnks = edf[ (edf.eye == 'B') & (edf.label == 'BLNK') ].dursec.median();

        print("BLINKS:");
        if(nlblnks > 1 ):
            print("  LEFT: {:4d} blnks / {:4.1f} secs ({:2.1f}/sec). DUR: {:4.1f} ({:4.1f}-{:4.1f})".format(nlblnks, dt*nleye_notna, nlblnks/(nleye_notna*dt), 1e3*medlblnks, 1e3*minlblnks, 1e3*maxlblnks) );
            pass;
        if(nrblnks > 1 ):
            print("  RGHT: {:4d} blnks / {:4.1f} secs ({:2.1f}/sec). DUR: {:4.1f} ({:4.1f}-{:4.1f})".format(nrblnks, dt*nreye_notna, nrblnks/(nreye_notna*dt), 1e3*medrblnks, 1e3*minrblnks, 1e3*maxrblnks) );
            pass;
        if(nbblnks > 1 ):
            print("  BINO: {:4d} blnks / {:4.1f} secs ({:2.1f}/sec). DUR: {:4.1f} ({:4.1f}-{:4.1f})".format(nbblnks, dt*nbeye_notna, nbblnks/(nbeye_notna*dt), 1e3*medbblnks, 1e3*minbblnks, 1e3*maxbblnks) );
            pass;

        
        
        pass;
    
    exit(0);
    pass;
