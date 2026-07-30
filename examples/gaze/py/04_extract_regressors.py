
import pandas as pd
import numpy as np
import sys

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
        
        ngood = (~mysadf['bad']).sum();
        nsamp = len(mysadf.index);
        ratgood=ngood/nsamp;
        if( ratgood > 0.6 ):
            print("SAMP: {:5d}/{:5d} = {:3.1f}%".format(ngood,nsamp, ratgood*100));
            print("  X={:2.1f} ({:2.1f})  Y={:2.1f} ({:2.1f})".format(mysadf.cgx_dva.mean(),
                                                                      mysadf.cgx_dva.std(),
                                                                      mysadf.cgy_dva.mean(),
                                                                      mysadf.cgy_dva.std(),
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
