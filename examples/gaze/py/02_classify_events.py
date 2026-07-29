
## REV: easier to make a "class" which takes a row (with specific names) and then it can access those with helper functions.
## E.g. based on what kind of file it is, get samples etc.? Can I add additional names?
##      So easiest thing is just to load the DF and it will create a chunk of classes?

import traceback
import pandas as pd;
import sys;
import os;
import peyeutils as pu;
import multiprocessing as mp;
#from multiprocessing import Pool;
#from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np;

from contextlib import contextmanager

import shutil

import pathlib

import time;

def prep_log_directory(log_dir_path):
    """Call this ONCE in the main thread before starting the pool."""
    log_path = pathlib.Path(log_dir_path)
    if log_path.exists():
        print("Clearing old log dir [{}]".format(log_path.as_posix()));
        shutil.rmtree(log_path) # Nuke old files and folder
        pass;
    print("Creating (clean) log dir [{}]".format(log_path.as_posix()));
    log_path.mkdir(parents=True, exist_ok=True) # Recreate empty folder
    return;

@contextmanager
def redirect_to_file(log_path : pathlib.Path ):
    # Create a 'logs' directory if it doesn't exist
    
    # Generate a unique log file using the current process ID
    log_path = pathlib.Path(log_path) / f"worker_{os.getpid()}.log"
    
    # Open the file and redirect Python's standard output streams
    with open(log_path, "a", buffering=1) as f:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = f
        sys.stderr = f
        try:
            yield;
        finally:
            # Restore the original terminal streams when finished
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            pass;
        pass;
    return;


'''
import os
# Force underlying C-libraries to use a single thread, preventing the pool deadlock
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
'''

'''
def init_worker():
    # Forces the child's text stream to flush after every single write
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    return;
'''

def process_events(rowdic):
    
    row=rowdic['row'];
    csvdir=rowdic['csvdir'];
    
    with redirect_to_file(rowdic['log_path']):

        print("++++++++ DOING FOR: ", row['samples_csv']); #,flush=True);
        
        if( row['edferror'] or not row['haseyetracking'] ):
            raise Exception("ERROR: Shouldn't be here?");
        
        samppath = os.path.join(csvdir, row['samples_csv']);
        df = pd.read_csv(samppath,);
        
        if(len(df.index) < 1 ):
            print(df);
            print("ERROR: Any non-NAN? ", np.any(np.isfinite(df.cgx_dva)));
            raise Exception("ERROR: File {}: Binocular data is length 0 (full data is {})".format(len(df.index), len(df.index)));
        
        if( 'dva_per_px' not in row ):
            dm=row['recinfo_VB_DM']
            ppm=row['recinfo_VB_PPM']
            dva_per_m = pu.utils.get_center_dva_per_meter( dm, ppm );
            dva_per_px = 1/ppm * dva_per_m;
            pass;
        else:
            dva_per_px = row['dva_per_px'];
            pass;
        
        #if(True):
        #    return row;
        
        #REV these "times" will be correct because they are just rle (run-length encoding) of samples.
        #REV: ah, why do I bother here? This creates "blink" from df, i.e. raw samples...
        
        #REV: this is not necessary because we already do this in "preprocess", and
        # params like dva/px and badocl are passed through.
        #blinkev = pu.preproc.blink_df_from_samples(df,
        #                                           badcol='bad',
        #                                           tcol='Tsec',
        #                                           xcol='cgx_dva',
        #                                           ycol='cgy_dva',
        #                                           eyecol='eye',
        #                                           dva_per_px=dva_per_px );
        #blinkev['method'] = 'blink';
        
        sr = row['sr_hzsec'];
        
        sdf, ev = pu.peyeutils.preproc_and_compute_events(
            df = df,
            tcol = 'Tsec',
            xcol = 'cgx_dva',
            ycol = 'cgy_dva',
            sr_hzsec = sr,
            mainseq_err_gain=1.5,
            PLOT=False,
        );

        #print("AT END");
        #print( ev[ (ev.eye=='R') & (ev.label=='BLNK')] );
        #ev = pd.concat( [ev, blinkev] );
        
        evfname = row['edffile'] + '.events2.csv'; #REV: need to add these after (I'm not saving over it)
        row['events2_csv'] = evfname;
        
        evpath = os.path.join( csvdir, evfname );
        ev.to_csv(evpath, index=False);
        
        print("+++++++ FINISHED FOR: ", row['samples_csv']); #,flush=True);
        pass; #With logfile thing.
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
    #MINTODO=490; #REV: I don't know which one "failed"...
    #MAXTODO=-1; #10; #-1;
    
    #todo = ['PYFREE_P012_SY_out_endrec_start_2024-08-14-15-27-55_end_2024-08-14-15-28-34.edf', 'PYFREE_FUKUDA_MIO_P007_endrec_start_2023-11-20-11-10-17_end_2023-11-20-11-10-23.edf', 'PYFREE_P012_SY_FMRI_endrec_start_2024-08-07-15-50-28_end_2024-08-07-15-56-43.edf', 'PYFREE_C338_FMRI_endrec_start_2025-11-10-13-42-55_end_2025-11-10-13-49-42.edf', 'PYFREE_FUJII_RIEKO_C313_endrec_start_2023-08-07-13-39-23_end_2023-08-07-13-46-52.edf', 'PYFREE_P012_SY_FMRI_endrec_start_2024-08-07-15-39-32_end_2024-08-07-15-46-23.edf', 'PYFREE_P012_SY_FMRI_endrec_start_2024-08-07-15-37-59_end_2024-08-07-15-38-36.edf', 'PYFREE_C338_FMRI_endrec_start_2025-11-10-14-25-16_end_2025-11-10-14-25-54.edf', 'PYFREE_P010_IY_FMRI_endrec_start_2024-04-17-13-58-30_end_2024-04-17-14-05-05.edf', 'PYFREE_P010_IY_FMRI_endrec_start_2024-04-17-13-44-50_end_2024-04-17-13-55-25.edf', 'PYFREE_P015_AF_FMRI_endrec_start_2024-11-28-10-47-16_end_2024-11-28-10-54-10.edf', 'PYFREE_C343_out_endrec_start_2026-01-21-11-09-41_end_2026-01-21-11-14-56.edf', 'PYFREE_C321_MS_FMRI_endrec_start_2024-04-11-11-45-38_end_2024-04-11-11-52-42.edf', 'PYFREE_C338_FMRI_endrec_start_2025-11-10-14-35-30_end_2025-11-10-14-42-14.edf', 'PYFREE_P010_IY_FMRI_endrec_start_2024-04-17-14-28-35_end_2024-04-17-14-29-45.edf', 'PYFREE_P012_SY_out_endrec_start_2024-08-14-15-36-53_end_2024-08-14-15-42-11.edf', 'PYFREE_FUJII_RIEKO_C313_endrec_start_2023-08-07-13-47-35_end_2023-08-07-13-54-33.edf']
    
    log_path='/scratch/worker_logs';
        
    prep_log_directory(log_path);
        
    rows=[ dict(row=row,csvdir=csvdir,log_path=log_path) for i,row in rowdf.iterrows() ];
    #if row['edffile'] in todo]
    
    
    print("Will proc for N EDFs: ", len(rows));
    
    
    #mp.set_start_method('spawn', force=True);

    starttime=time.time();
    
    MULTIPROC=True;
    NPROC=48;
    results=list();
    if(MULTIPROC):
        #with ProcessPoolExecutor(max_workers=NPROC) as executor:
        with mp.Pool(processes=NPROC) as pool:
                     #, initializer=init_worker)
            
            #try:
            #results = list(executor.map(process_events, rows, chunksize=1));
            #futures = {executor.submit(process_events, row): row for row in rows};
            #results = list(executor.map(process_events, rows, chunksize=1));
            #results = pool.map(process_events, rows);
            #    pass;
            #except Exception as e:
            #    
            #    raise Exception("(MULTIPROC EXCEPTION): {}".format(e));
            try:
                futures = pool.imap_unordered(process_events, rows);
                for result in futures:
                    results.append(result);
                    elapsed=time.time()-starttime;
                    print("{:6.1f}s   {:6d}/{:6d} ({:4.1f}%) -- Finished [{}]".format(elapsed, len(results), len(rows), len(results)/len(rows)*100, result['edffile']));
                pass;
            except Exception as e:
                traceback.print_exc();
                print(f"Exception caught: {e}. Force-terminating all workers immediately.")
                
                # 2. Native, safe kill method (No PID hacking required)
                pool.terminate()
                
                # 3. Clean up the process table so no zombies are left
                pool.join()
                
                raise e;
            pass;
        pass;
    else:
        for rowdict in rows:
            results.append( process_events( rowdict ) );
            pass;
        print("Single threaded -- finished all rows");
        pass;
    
    print("Length of results: {}".format(len(results)));
    rowdf = pd.DataFrame(results);
    print(rowdf);
    outfn=rowcsv+'.w_events2.csv';
    print("Outputting CSV to {}".format(outfn));
    rowdf.to_csv(outfn, index=False);
    
    
    return 0;

if __name__=='__main__':
    exit(main());

