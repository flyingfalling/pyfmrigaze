
## REV: easier to make a "class" which takes a row (with specific names) and then it can access those with helper functions.
## E.g. based on what kind of file it is, get samples etc.? Can I add additional names?
##      So easiest thing is just to load the DF and it will create a chunk of classes?

import pandas as pd;
import sys;
import os;
import peyeutils as pu;
from multiprocessing import Pool;
import numpy as np;

def process_events(rowdic):
    row=rowdic['row'];
    csvdir=rowdic['csvdir'];
    
    if( row['edferror'] or not row['haseyetracking'] ):
        raise Exception("Shouldn't be here?");
    
    samppath = os.path.join(csvdir, row['samples_csv']);
    df = pd.read_csv(samppath);

    if(len(df.index) < 1 ):
        print(df);
        print("Any non-NAN? ", np.any(np.isfinite(df.cgx_dva)));
        raise Exception("File {}: Binocular data is length 0 (full data is {})".format(len(df.index), len(df.index)));

    if( 'dva_per_px' not in row ):
        dm=row['recinfo_VB_DM']
        ppm=row['recinfo_VB_PPM']
        dva_per_m = pu.utils.get_center_dva_per_meter( dm, ppm );
        dva_per_px = 1/ppm * dva_per_m;
        pass;
    else:
        dva_per_px = row['dva_per_px'];
        pass;

    
    
    #REV these "times" will be correct because they are just rle (run-length encoding) of samples.
    blinkev = pu.preproc.blink_df_from_samples(df,
                                               badcol='bad',
                                               tcol='Tsec',
                                               xcol='cgx_dva',
                                               ycol='cgy_dva',
                                               eyecol='eye',
                                               dva_per_px=dva_per_px );
    blinkev['method'] = 'blink';
    
    sr = row['recinfo_samplerate'];
    
    sdf, ev = pu.peyeutils.preproc_and_compute_events(
        df = df,
        tcol = 'Tsec',
        xcol = 'cgx_dva',
        ycol = 'cgy_dva',
        sr_hzsec = sr,
        mainseq_err_gain=1.5,
        PLOT=False,
    );
    
    ev = pd.concat( [ev, blinkev] );
    
    evfname = row['edffile'] + '.events2.csv';
    row['events2_csv'] = evfname;
    
    evpath = os.path.join( csvdir, evfname );
    ev.to_csv(evpath, index=False);
    
    return row; #Oh, this will not be a 1-row DF...

'''
def plotrow(rowdic):
    row=rowdic['row'];
    csvdir=rowdic['csvdir'];
    
    samppath = os.path.join(csvdir, row['samples_csv']);
    evpath = os.path.join(csvdir, row['events2_csv']);
    trialspath = os.path.join(csvdir, row['trials_csv']);

    samps = pd.read_csv(samppath);
    ev = pd.read_csv(evpath);

    print(ev);
    print(ev[ev['label']=='SACC']);
    trials = pd.read_csv(trialspath);
    print(samps.columns);
    print(ev.columns);
    print(trials.columns);
    tokeep=['edffile', 'name', 'kind']
    print(row.keys());
    titlerow=[ row[k] for k in row.keys() if k in tokeep ];
    for i,fig in enumerate(
            pu.plotting.plot_gaze_chunks( df=samps, timestamp_col='Tsec',
                                          x_col='cgx_dva', y_col='cgy_dva',
                                          chunk_size_sec=5,
                                          events_df=ev,
                                          event_start_col='stsec',
                                          event_end_col='ensec',
                                          event_type_col='label',
                                          stimulus_df=trials,
                                          stim_start_col='start_s',
                                          stim_end_col='end_s',
                                          stim_name_col='video',
                                          max_chunks_per_fig=5,
                                          ylim=7,
                                          proplist=titlerow )
            ):
        figbase=os.path.join( csvdir, row['edffile'] );
        fn = figbase + '_timeplot_{:04d}.pdf'.format(i)
        print("Saving [{}]".format(fn));
        fig.savefig(fn);
        pass;
        
    return;
'''

def main():
    rowcsv = sys.argv[1];
    csvdir = sys.argv[2];
    
    rowdf = pd.read_csv(rowcsv); #REV: e.g. allfmriedfs.csv
    
    #REV: sanity check -- these should almost never happen at all and may alrady be dropped
    rowdf = rowdf.loc[ (rowdf['haseyetracking'] & (False==rowdf['edferror'])) ];
    #rowdf = rowdf[:5];
    results = list();
    rows=[ dict(row=row,csvdir=csvdir) for i,row in rowdf.iterrows() ];
    
    
    MULTIPROC=True;
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
    
    #for i, row in rowdf.iterrows():
    #    plotrow(dict(row=row, csvdir=csvdir) );
    #    pass;
    
    return 0;

if __name__=='__main__':
    exit(main());

