
import pandas as pd
import numpy as np
import sys

import numpy as np
from scipy.stats import gaussian_kde

def compute_kde_continuous_entropy(x_coords, y_coords, sample_grid_res=50,
                                   screen_width, screen_height):
    """
    Computes continuous gaze entropy using non-parametric Kernel Density Estimation.
    Independent of raw sample size.
    """
    x = np.asarray(x_coords)
    y = np.asarray(y_coords)
    valid = ~np.isnan(x) & ~np.isnan(y)
    x, y = x[valid], y[valid];
    
    if len(x) < 5:  # KDE requires a baseline number of points to estimate bandwidth
        return 0.0
    
    # Fit the continuous probability density function
    positions = np.vstack([x, y])
    kernel = gaussian_kde(positions)
    
    # Create a uniform evaluation mesh across the screen space
    X, Y = np.meshgrid(np.linspace(0, screen_width, sample_grid_res),
                       np.linspace(0, screen_height, sample_grid_res))
    mesh_positions = np.vstack([X.ravel(), Y.ravel()])
    
    # Evaluate density at each mesh intersection point
    pdf_values = kernel(mesh_positions)
    
    # Normalize density so it integrates to 1 over the area element
    dx = screen_width / (sample_grid_res - 1)
    dy = screen_height / (sample_grid_res - 1)
    dA = dx * dy
    
    # Avoid log(0)
    pdf_values = pdf_values[pdf_values > 1e-10]
    
    # Continuous entropy calculation via Riemann sum approximation
    kde_entropy = -np.sum(pdf_values * np.log(pdf_values)) * dA
    return kde_entropy



def main():
    trialscsv=sys.argv[1];
    eventscsv=sys.argv[2];
    samplscsv=sys.argv[3];
    
    trdf = pd.read_csv(trialscsv);
    evdf = pd.read_csv(eventscsv);
    sadf = pd.read_csv(samplscsv);
    
    print(trdf);
    print(trdf.ispract);
    print(trdf.rest);
    
    trdf = trdf[ (trdf.ispract == 'no') & ~trdf.rest.isin(['pre','post']) ].copy().reset_index(drop=True);
    
    print(trdf);
    
    print(evdf);
    evdf = evdf[ (evdf.ispract=='no') & ~evdf.rest.isin(['pre','post']) & evdf.label.isin(['SACC','ISI','BLNK']) ].copy().reset_index(drop=True);
    print(evdf);

    sadf = sadf[ (sadf.ispract=='no') & ~sadf.rest.isin(['pre','post']) ].copy().reset_index(drop=True);
    
    indexercols=['name', 'blkidx', 'trialidx', 'video', 'grp', 'APPA', 'edffile'];
    print("TRIALS");
    print(trdf);
    print("COLS: ", trdf.columns);
    trdf['myidx'] = trdf[ indexercols
                         ].astype(str).apply('-'.join, axis=1);
    evdf['myidx'] = evdf[ indexercols
                         ].astype(str).apply('-'.join, axis=1);
    sadf['myidx'] = sadf[ indexercols
                         ].astype(str).apply('-'.join, axis=1);
    
    trgrps = trdf.groupby('myidx');
    evgrps = evdf.groupby('myidx');
    sagrps = sadf.groupby('myidx');

    print( "TR {}   EV {}  SR {}".format(len(trgrps.groups), len(evgrps.groups), len(sagrps.groups), ));

    
    for key in trgrps.groups:
        mytrdf=trgrps.get_group(key);

        print();
        print(key);
        
        if( key not in sagrps.groups ):
            raise Exception("Wtf has trial but not samples? [{}]".format(key));

        mysadf=sagrps.get_group(key);

        #REV: shit, I will need to make a separate variable for each video! I.e. clip_01_xmean etc.
        ## That way it can compare. Otherwise it will use the video identity to do classification.
        
        lensec=mysadf.Tsec.max() - mysadf.Tsec.min();
        ngood = (~mysadf['bad']).sum();
        nsamp = len(mysadf.index);
        ratgood=ngood/nsamp;
        goodsecs = ratgood * lensec;
        thresh=0.5;
        if( ratgood > thresh ): #REV: how "much" of a trial do they need to "watch" lol.
            print("SAMP: {:5d}/{:5d} = {:3.1f}%".format(ngood,nsamp, ratgood*100));
            #REV: don't use pupil (PA) as it is not normalized yet and so may give away subject.
            #(raw pupil area some subjects bigger pupils or closer/further position or different
            # ambient).
            print("  X={:2.1f} ({:2.1f})  Y={:2.1f} ({:2.1f}),  PUPIL:{:2.1f} ({:2.1f})".format(
                mysadf.cgx_dva.mean(),
                mysadf.cgx_dva.std(),
                mysadf.cgy_dva.mean(),
                mysadf.cgy_dva.std(),
                mysadf.pa_lpf.mean(),
                mysadf.pa_lpf.std(),
            ));
        else:
            print("Insufficient SAMPLES");
        
        if( key not in evgrps.groups ):
            #print(mysadf[['Tsec', 'cgx_dva', 'cgy_dva']]);
            
            #import matplotlib.pyplot as plt;
            #plt.plot(mysadf.Tsec, mysadf.cgx_dva, label='x');
            #plt.plot(mysadf.Tsec, mysadf.cgy_dva, label='y');
            #plt.legend();
            #plt.savefig('test.pdf');
            #raise Exception("Wtf has trial but not events? [{}]".format(key));
            print("No events for [{}]".format(key));
            pass;
        else:
            myevdf=evgrps.get_group(key);
            
            print("SACC: {:3d}".format( len(myevdf[myevdf.label=='SACC'].index)) );
            print("ISI:  {:3d}".format( len(myevdf[myevdf.label=='ISI'].index)) );
            print("BLNK: {:3d}".format( len(myevdf[myevdf.label=='BLNK'].index)) );
            pass;
        
    return 0;

if __name__=='__main__':
    exit(main());
    pass;
