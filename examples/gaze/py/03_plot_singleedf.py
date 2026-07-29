
import pandas as pd
import numpy as np
import peyeutils as pu

import sys;
import os;

def main():

    edf = sys.argv[1];

    eyes=['B'];

    sampcsv = edf + '.samples.csv';
    evcsv = edf + '.events2.csv';
    
    sdf = pd.read_csv(sampcsv);
    ev = pd.read_csv(evcsv);
    
    tcol='Tsec';
    xcol='cgx_dva';
    ycol='cgy_dva';
    pupil_col= 'pa';
    eyecol='eye';
    
    for i,fig in enumerate(
            pu.plotting.plot_gaze_chunks_wpupil( df=sdf, timestamp_col=tcol, x_col=xcol, y_col=ycol, chunk_size_sec=10,
                                                 events_df=ev, event_start_col='stsec', event_end_col='ensec',
                                                 event_type_col='label', max_chunks_per_fig=4,
                                                 pupil_col=pupil_col, eyes_to_plot=eyes, eye_col=eyecol
                                                )
    ):
        fig.savefig('testfig_{:04d}.pdf'.format(i));
        pass;
    
    return 0;

if __name__=='__main__':
    exit(main());
    pass;
