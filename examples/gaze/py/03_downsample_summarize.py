import pandas as pd
import numpy as np
import sys;
import os;
import peyeutils as pu;



# Reads all EDF data.
#  1) Downsamples to e.g. 100 Hz
#  2) Extracts by BLOCK, TRIAL,
#  3) Marks "trial numbers" (and block numbers) on each event, with their start-time and time from FMRIstart and BLOCKstart
#  4) pre/post rest periods are included.
#  5) Saves new "trials" list with trial_no. Specifies stats like good data points/out for each trial. Nsacc, Nisi, etc.?
##    -> This is basically summary already haha. I can do that after. Note, problem is that I need to remove "unrealistic" blinks, e.g.
##       blinks which are too long, e.g. > 500 msec? Just sum all events to get total time?


if __name__=='__main__':
    
    alledfs=sys.argv[1];
    csvdir=sys.argv[2];

    vidconddf = pd.read_csv('vidcondgrps.csv');
    print(vidconddf);
    
    df = pd.read_csv(alledfs);
    df = df.sort_values( by = ['name', 'kind'], ignore_index=True );
    print("Subjs B4: ", df.name.unique());
    
    df = df[ ((df['name'].str.startswith('C')) & (df['name'] >= 'C309')) |
             ((df['name'].str.startswith('P')) & (df['name'] >= 'P001'))   ];

    newalltrialsrests=list();
    #newallblocks=list();
    newallevents=list();
    #newallrests=list();
    newallsamps=list();

    sampkeepcols=['Tsec', 'bad',
                  'cgx_px', 'cgy_px', 'cgx_dva', 'cgy_dva',
                  'pa_lpf',
                  ];

    evkeepcols=['stsec', 'ensec', 'stx', 'sty', 'enx', 'eny', 'pvel', 'medvel',
                'avgvel', 'label', 'dydva',
                'dxdva', 'dursec', 'angle', 'ampldva',
                'eye', 'source', 'idx', 'stidx', 'enidx', 'ismain',
                ];
    
    rowkeepcols=['name', 'edfdatetime', 'edffile',];

    trialkeepcols=['start_s', 'end_s', 'video', 'vidw_px', 'vidh_px', 'vidxpos_px', 'vidypos_px',
                   'fmrist_s','fmri_offset_s', 'trialidx', 'blkidx', 'rest', #'tcol',
               ];

    blkkeepcols=['blkstart_s', 'blkend_s', 'blkidx', 'ispract', #'tcol',
                 'APPA', 'grp'
             ];
    
    keepcols = sampkeepcols + evkeepcols + rowkeepcols + trialkeepcols + blkkeepcols;

    keepcols = list(set(keepcols)); #REV remove duplicates.
    
    
    print("Filtered: ", df.name.unique());
    
    df = df[ (df.kind=='outside') ];

    #REV: first 20.
    df = df.iloc[:20];
    
    rows=list();
    for i,row in df.iterrows():

        print("ROW COLUMNS: ", row.keys());
        
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
        print("  [{}]  [{}] trials, [{}] blks".format(origedf, ntrials, nblocks));
        
        

        if( hasgaze ):
            edf = pd.read_csv( os.path.join(csvdir, myevents ) );
            sdf = pd.read_csv( os.path.join(csvdir, mysamples) );

            print("Using only eye [B]");
            edf = edf[ edf.eye=='B' ].sort_values(by='stsec').reset_index(drop=True);
            sdf = sdf[ sdf.eye=='B' ].sort_values(by='Tsec').reset_index(drop=True);

            ## DOWNSAMPLE!!
            sr_downsampled = 100;
            #REV: can my resample work this way?
            
            #REV: sdf_down can no longer trust non-float values.
            #REV: for example, "bad", "LABEL", etc. will not be representative of contents.
            #REV: in that sense, better to just "drop" every Nth value rather than rolling mean...

            '''
            sdf_down2 = pu.utils.interpolate_df_to_samplerate(sdf,
                                                             'Tsec',
                                                             sr_downsampled,
                                                             tcolunit_s=1,
                                                             zeroTsec=sdf.Tsec.min(),
                                                             );
            '''
            mysr=1000;
            sdf=sdf.reset_index(drop=True);
            keep_Nth=20; #= mysr/sr_downsampled
            sdf_down = sdf.iloc[::keep_Nth, :];
            #sdf_down2 = sdf[sdf.reset_index().index % keep_Nth == 0].reset_index(drop=True); #sdf.iloc[::keep_Nth, :];
            #print(sdf_down);
            print("SAMP COLUMNS: ", sdf_down.columns);
            pass;
        
        
        print(blockdf.columns);
        for bi, brow in blockdf.iterrows():
            print("Block {:4d}  [{:5.1f} - {:5.1f}] (dur: {:3.1f} sec)  (FMRI start: {:5.1f})".format(brow.blkidx, brow.blkstart_s, brow.blkend_s, brow.blkend_s-brow.blkstart_s, brow.fmrist_s));
            
            mytrialsdf = trialdf[ trialdf.blkidx == brow.blkidx ].copy();
            
            
            print(mytrialsdf.columns);
            mytrialsdf = mytrialsdf.sort_values(by='start_s');
            mytrialsdf = pd.merge( left=mytrialsdf,
                                 right=vidconddf,
                                 left_on='video',
                                 right_on='vid',
                                 how='left');
            if( mytrialsdf['grp'].isna().sum() > 0 ):
                raise Exception("Failed! Unrecognized video?");

            mygrp = mytrialsdf['grp'].unique();
            if(len(mygrp) != 1 ):
                raise Exception("Not just one group? {}".format(mygroup));

            blkinfo=mytrialsdf.iloc[0];
            mygrp=blkinfo['grp'];
            myappa=blkinfo['APPA'];
            ispract=blkinfo['ispract'];
            
            brow['grp'] = mygrp;
            brow['APPA'] = myappa;
            brow['ispract'] = ispract;
            
            mytrialsdf['rest'] = '';
            
            #REV: set missing values from block, easier than joining because lot sof overlap
            # btw columns already...
            for c in brow.keys():
                if c not in mytrialsdf.columns:
                    mytrialsdf[c] = brow[c];
                    pass;
                pass;
            
            
                
            
            for c in row.keys():
                #print("{}".format(c));
                if c not in mytrialsdf.columns:
                    print("Setting all trial [{}] to {}".format(c, row[c]));
                    mytrialsdf[c] = row[c];
                    pass;
                pass;

            
            
            firsttrial = mytrialsdf.iloc[0];
            lasttrial = mytrialsdf.iloc[-1];
            print("Got {} trials  (GRP: {}  APPA: {}  PRACT: {})".format(len(mytrialsdf.index), mygrp, myappa, ispract));
            print("First trial from BLKSTART: {:3.1f}   from FMRISTART: {:3.1f} (FMRI offset was: {:3.1f})".format(firsttrial.start_s - brow.blkstart_s, firsttrial.start_s - brow.fmrist_s, firsttrial.fmri_offset_s));
            
            rest1_st = brow.fmrist_s;
            rest1_en = firsttrial.start_s;
            
            
            prerest_row = dict(rest='pre',
                               trialidx=-1,
                               video='',
                               ispract=brow.ispract,
                               #
                               start_el=brow.fmrist_el,
                               start_s=brow.fmrist_s,
                               #start_wall=brow.fmrist_wall,
                               end_el=firsttrial.start_el,
                               end_s=firsttrial.start_s,
                               #end_wall=firsttrial.start_wall,
                               #
                               isfmri=firsttrial.isfmri,
                               fmrist_el=firsttrial.fmrist_el,
                               fmrist_s=firsttrial.fmrist_s,
                               #fmrist_wall=firsttrial.fmrist_wall,
                               blkstart_el=firsttrial.blkstart_el,
                               blkstart_s=firsttrial.blkstart_s,
                               blkend_el=firsttrial.blkend_el,
                               blkend_s=firsttrial.blkend_s,
                               fmri_offset_el=firsttrial.fmri_offset_el,
                               fmri_offset_s=firsttrial.fmri_offset_s,
                               #fmri_offset_wall=firsttrial.fmri_offset_wall,
                               blkidx=firsttrial.blkidx,
                               tcol=firsttrial.tcol,
                               haseyetracking=firsttrial.haseyetracking,
                               );
            
            rest2_st = lasttrial.end_s;
            rest2_en = brow.blkend_s;
            
            
            postrest_row = dict(rest='post',
                                trialidx=-1,
                                video='',
                                ispract=brow.ispract,
                                #
                                start_el=lasttrial.end_el,
                                start_s=lasttrial.end_s,
                                #start_wall=lasttrial.end_wall,
                                end_el=brow.blkend_el,
                                end_s=brow.blkend_s,
                                #end_wall=brow.blkend_wall,
                                #
                                isfmri=firsttrial.isfmri,
                                fmrist_el=firsttrial.fmrist_el,
                                fmrist_s=firsttrial.fmrist_s,
                                #fmrist_wall=firsttrial.fmrist_wall,
                                blkstart_el=firsttrial.blkstart_el,
                                blkstart_s=firsttrial.blkstart_s,
                                blkend_el=firsttrial.blkend_el,
                                blkend_s=firsttrial.blkend_s,
                                fmri_offset_el=firsttrial.fmri_offset_el,
                                fmri_offset_s=firsttrial.fmri_offset_s,
                                #fmri_offset_wall=firsttrial.fmri_offset_wall,
                                blkidx=firsttrial.blkidx,
                                tcol=firsttrial.tcol,
                                haseyetracking=firsttrial.haseyetracking,
                                );
            
            print("Rest 1 {:4.1f}-{:4.1f} ({:3.1f} sec)".format(rest1_st, rest1_en, rest1_en-rest1_st));
            print("Rest 2 {:4.1f}-{:4.1f} ({:3.1f} sec)".format(rest2_st, rest2_en, rest2_en-rest2_st));
            
            myrests = pd.DataFrame([ prerest_row, postrest_row]);

            for c in brow.keys():
                if( c not in myrests ):
                    myrests[c] = brow[c];
                    pass;
                pass;
            
            
            #newallrests.append(myrests);
            
            #REV: concat with rests
            mytrialsrests = pd.concat( [mytrialsdf, myrests], ignore_index=True );
            
            mytrialsrests = mytrialsrests[ [c for c in mytrialsrests.columns if c in keepcols] ];

            
            newalltrialsrests.append(mytrialsrests);
            
            #REV: this could include noise at beginning of blah
            #REV: better to just take all videos and rests inside of it.
            #blkevents = edf[ edf.stsec >= brow ];
            if( (False == hasgaze) or (True == edferr ) ):
                print("Skipping adding events (no gaze)");
                continue;
            
            for ti, trow in mytrialsrests.iterrows():
                #REV: this will miss things "between" trials. Oh well.
                myev = edf[ (edf.stsec >= trow.start_s) &
                            (edf.ensec <= trow.end_s)
                           ].copy();

                mysamps = sdf_down[ (sdf_down.Tsec >= trow.start_s) &
                                    (sdf_down.Tsec <= trow.end_s)
                                   ].copy();
                
                #n_notbad = len( mysamps[ (mysamps.bad == False) ].index ); #REV: or just sum ISI?
                
                #REV: combine with events.
                for c in trow.keys():
                    if( c not in myev.columns ):
                        myev[c] = trow[c];
                        mysamps[c] = trow[c];
                        pass;
                    pass;


                myev = myev[ [c for c in myev.columns if c in keepcols] ];
                mysamps = mysamps[ [c for c in mysamps.columns if c in keepcols] ];
                newallevents.append(myev);
                newallsamps.append(mysamps);
                pass;
            

            #REV: should read samples here too, and combine, use for "good" data etc...
            
            pass; #REV: end for all blocks
        
        
        if(True):
            continue;
        
        
        #edf = pd.read_csv( os.path.join(csvdir, myevents ) );
        
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

    trialsrests = pd.concat(newalltrialsrests, ignore_index=True);
    events = pd.concat(newallevents, ignore_index=True);
    samps = pd.concat(newallsamps, ignore_index=True);
    
    trialsrests.to_csv('summarized_trialsrests.csv', index=False);
    events.to_csv('summarized_events.csv', index=False);
    samps.to_csv('summarized_samps.csv', index=False);
    exit(0);
    pass;
