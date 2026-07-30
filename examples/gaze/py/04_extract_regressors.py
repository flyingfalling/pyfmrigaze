
import pandas as pd
import numpy as np
import sys

def main():
    trialscsv=sys.argv[1];
    eventscsv=sys.argv[2];

    trdf = pd.read_csv(trialscsv);
    evdf = pd.read_csv(eventscsv);
    sadf = pd.read_csv(samplscsv);
    
    print(trdf);
    trdf = trdf[ (trdf.ispract == 'no') & (trdf.rest == '') ];
    print(trdf);
    
    print(evdf);
    evdf = evdf[ evdf.label.isin(['SACC','ISI','BLNK']) ];
    print(evdf);
    
    indexercols=['name', 'blkidx', 'trialidx', 'video', 'grp', 'APPA',];
    trdf['myidx'] = trdf[ indexercols
                       ].astype(str).agg('-'.join(), axis=1);
    evdf['myidx'] = evdf[ indexercols
                       ].astype(str).agg('-'.join(), axis=1);
    sadf['myidx'] = sadf[ indexercols
                       ].astype(str).agg('-'.join(), axis=1);

    trgrps = trdf.groupby(level='myidx');
    evgrps = evdf.groupby(level='myidx');
    sagrps = evdf.groupby(level='myidx');
    
    for key in trgrps.groups:
        if( key not in evgrps.groups ):
            raise Exception("Wtf has trial but not events? [{}]".format(key));
        if( key not in sagrps.groups ):
            raise Exception("Wtf has trial but not samples? [{}]".format(key));
        
        mytrdf=trgrps.get_group(key);
        myevdf=evgrps.get_group(key);
        mysadf=sagrps.get_group(key);
        
        print("SACC: ", len(mytrdf[mytrdf.label=='SACC'].index));
        print("ISI: ", len(mytrdf[mytrdf.label=='ISI'].index));
        print("BLNK: ", len(mytrdf[mytrdf.label=='BLNK'].index));
        pass;
    
    return 0;

if __name__=='__main__':
    exit(main());
    pass;
