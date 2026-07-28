import pandas as pd
import numpy as np
import sys;
import os;

if __name__=='__main__':
    
    alledfs=sys.argv[1];
    csvdir=sys.argv[2];
    
    df = pd.read_csv(alledfs);

    cols=list();
    rows=list();
    for i,row in df.iterrows():
        mysamps=row['samples_csv'];
        samppath=os.path.join(csvdir, mysamps);
        
        if( not os.path.isfile(samppath) ):
            raise Exception("Expected samples missing [{}]".format(samppath));
        
        sdf = pd.read_csv(samppath, nrows=10);
        cols.append(list(sdf.columns));
        
        pass;
    
    sizes = [ len(l) for l in cols ];
    biggest = max(sizes);
    smallest = min(sizes);
    print("Biggest list is {} (smallest={})".format(biggest, smallest));
    flatcols = [ c for sublist in cols for c in sublist ];
    uniques = set(flatcols);
    if( len(uniques) != biggest ):
        raise Exception("Set not same size...");

    print("Bad cols: [{}]".format( [c for c in uniques if 'bad' in c ] ) );
    
    #rowdf = pd.DataFrame(rows);
    #print(rowdf);
    
    #rowdf.to_csv(alledfs + '_w_events2.csv', index=False);
    exit(0);
    pass;
