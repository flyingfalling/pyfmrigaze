## REV: computes saliency of gaze target and random controls.
##      random controls is simply mean density of gaze of subject during any video (easier
##      than any-but-this-video), i.e. looking prior.

## Downsample to frame-rate of video (mean?). Exclude saccs/blinks.
## Do some 3d tensor of frame over time, and sample from X/Y pos inside it. Convolution with something perhaps.
## Just use null (prior) distribution, and multiply by saliency to get value.



## Also: chunk/export individual trials as CSVs (easier). Or e.g. npy or etc.
## Also: do full pairwise correlation, and plot individual trials all together (as single-row).


## Decoding/Encoding based no only on saliency, but based on Deep CNN (e.g. alexnet), on same inputs.


def gaze_saliency(trial):
    
    return;

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
    
    
    print("TRIALS");
    print(trdf);
    print("COLS: ", trdf.columns);
    
    indexercols=['name', 'blkidx', 'trialidx', 'video', 'grp', 'APPA', 'edffile'];
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
    
    
    subjvids=list();
    
    for key in trgrps.groups:
        mytrdf=trgrps.get_group(key);
        subj=mytrdf.iloc[0]['name'];
        vid=mytrdf.iloc[0]['video'];
        myidx=mytrdf.iloc[0]['myidx'];

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
        subjvids.append( dict(subj=subj, vid=vid, goodsecs=goodsecs, myidx=myidx,) );
        pass;
        
    subjvids = pd.DataFrame( subjvids );
    vidstoview = trdf[ trdf['grp'].isin(['C', 'D']) ]; # fix group! and not practice
    vidstoview = vidstoview.video.unique();
    print(vidstoview, len(vidstoview));
    
    
    
    return 0;

