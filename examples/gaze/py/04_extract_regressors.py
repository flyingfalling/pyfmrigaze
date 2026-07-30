
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import seaborn as sns

import numpy as np
from scipy.stats import gaussian_kde

def make_heatmap(subjvids):
    print(len(subjvids.subj.unique()));
    print(len(subjvids.vid.unique()));

    all_subjects = sorted(subjvids['subj'].dropna().unique())
    all_videos = sorted(subjvids['vid'].dropna().unique())
    
    print(f"Target Dimensions -> Subjects: {len(all_subjects)} | Videos: {len(all_videos)}")
    
    FULL=True;
    if(FULL):
        # 2. Pivot using a method that safely keeps unique pairings
        pivot_raw = subjvids.pivot_table(
            index='subj',
            columns='vid',
            values='goodsecs',
            aggfunc='max'
        )
        
        # 3. FORCE the matrix to physically span across all 59 subjects and 60 videos
        # Any blank cross-sections will explicitly become 0 instead of shrinking the grid
        pivot_full = pivot_raw.reindex(index=all_subjects, columns=all_videos, fill_value=0)
        print(f"Verified Matrix Form: {pivot_full.shape}") # Will strictly output (59, 60)

        pivot_full = pivot_full.sort_index().fillna(0).astype(float)

        # Verify no NaNs or Infs remain in the data structure
        assert np.isfinite(pivot_full.values).all(), "Data still contains non-finite values!"


        # Create a clean, standard figure canvas
        fig, ax = plt.subplots(figsize=(18, 12))

        # Use standard heatmap to eliminate hidden dendrogram margins
        sns.heatmap(
                pivot_full,
                ax=ax,
                cmap="viridis",
                cbar_kws={
                            "label": "Watch Time (goodsecs)",
                            "location": "left",  # Places colorbar perfectly on the left edge
                            "shrink": 0.4,  # Adjusts vertical height of the colorbar
                        },
                linewidths=0.05,
                linecolor="#444444",
                xticklabels=True,
                yticklabels=True,
            )
                
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position("right")

        # FORCE standard 90-degree vertical orientation across all active ticks
        ax.tick_params(axis='y', labelsize=8, rotation=0)
        
        # Move the y-axis labels to the right side if the colorbar blocks them
        
        

        # Adjust margins to give text labels breathing room
        plt.subplots_adjust(bottom=0.25, right=0.92, left=0.1)

        '''
        # 4. Draw the uncorrupted 59x60 grid
        g = sns.clustermap(
            pivot_full,
            cmap="viridis",
            row_cluster=False,   # Disable vertical subject clustering
            col_cluster=False,   # Disable horizontal video clustering
            cbar_kws={"label": "Watch Time (goodsecs)"},
            cbar_pos=(0.02, 0.5, 0.02, 0.2),
            figsize=(18, 12),
            linewidths=0.05,       # Keeps grid partitions extremely sharp
            linecolor="#444444",   # Visible divider lines between adjacent cells
            xticklabels=True,      # Disables automatic column truncation
            yticklabels=True       # Disables automatic row truncation
        )
        
        # 5. Prevent label cutoff at the canvas margins
        plt.subplots_adjust(bottom=0.25, left=0.18)
        '''
        pass;

    else:
        
        
        ######## HEATMAP #########
        # 1. Clean and aggregate to get the maximum trial watch time
        df_clean = subjvids.dropna(subset=["goodsecs"])
        df_max_trial = df_clean.loc[
            df_clean.groupby(["subj", "vid"])["goodsecs"].idxmax()
        ]
        
        # 2. Pivot into a subject-by-video matrix
        pivot_df = df_max_trial.pivot(index="subj", columns="vid", values="goodsecs")
        
        # 3. Fill missing values with 0 (unwatched videos)
        pivot_df_filled = pivot_df.fillna(0)
        
        # 4. Plot the hierarchical clustered heatmap
        g = sns.clustermap(
            pivot_df_filled,
            cmap="viridis",  # Dark blue (0s) to bright yellow (max watch time)
            cbar_kws={"label": "Watch Time (goodsecs)"},
            figsize=(14, 10),
            linewidths=0.1,
            linecolor="gray",
        )
        
        # Styling and adjustments
        plt.setp(g.ax_heatmap.get_xticklabels(), rotation=90, fontsize=9)
        plt.setp(g.ax_heatmap.get_yticklabels(), rotation=0, fontsize=9)
        g.fig.suptitle(
            "Subject vs. Video Watch Times (Clustered Profile)",
            fontsize=16,
            fontweight="bold",
            y=1.02,
        )
        pass;
    
    plt.savefig('subj_vid_watched_heatmap.pdf');
    return;

def make_tradeoff_curves(subjvids):
    ######## TRADEOFF CURVE ##########
    
    
    # 1. Ensure data is aggregated and pivoted (from your 'subjvids' DataFrame)
    df_clean = subjvids.dropna(subset=['goodsecs'])
    df_max_trial = df_clean.loc[df_clean.groupby(['subj', 'vid'])['goodsecs'].idxmax()]
    pivot_df = df_max_trial.pivot(index='subj', columns='vid', values='goodsecs')
    
    # 2. Set up the figure
    plt.figure(figsize=(12, 7))
    
    # Define the exact time lines you want to compare (e.g., 1 to 10 seconds)
    seconds_to_plot = range(1, 10)
    subject_counts = np.arange(1, len(pivot_df) + 1, 1)
    
    # 3. Calculate and plot a line for each second interval
    for t in seconds_to_plot:
        matrix_t = (pivot_df > t).astype(int)
        
        # Sort subjects by total videos watched at this threshold
        sorted_subjs = matrix_t.sum(axis=1).sort_values(ascending=False).index
        
        video_counts = []
        for s_count in subject_counts:
            sub_subset = matrix_t.loc[sorted_subjs[:s_count]]
            shared_vids = (sub_subset.sum(axis=0) == s_count).sum()
            video_counts.append(shared_vids)
            pass;
        # Plot the line for the current second threshold
        plt.plot(subject_counts, video_counts, label=f'{t} seconds', marker='o', markersize=3)
        pass;
    
    # 4. Styling the 2D plot for scannability
    plt.title('Video Survival Curves across Subject Counts', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Number of Subjects Kept (Most Active → Least Active)', fontsize=12)
    plt.ylabel('Number of Videos Watched by ALL Kept Subjects', fontsize=12)
    
    plt.xticks(subject_counts, rotation=90) # Show every subject increment on X axis
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(title='Watch Threshold', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.savefig('time_subjects_vids_tradeoff.pdf');
    
    return;


def compute_kde_continuous_entropy(x_coords, y_coords, 
                                   screen_width, screen_height,
                                   sample_grid_res=50,):
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
    
    # Filter for valid views, group by video, and keep videos matching the total subject count
    # 1. Count videos per subject (with >= 6 seconds)
    subjvids = subjvids[ subjvids.vid.isin(vidstoview) ];
    
    
    
    print("SUBJVIDS");
    print(subjvids);
        
    subjvids = subjvids.loc[subjvids.groupby(['subj', 'vid'])['goodsecs'].idxmax()]
    
    make_heatmap(subjvids);    
    make_tradeoff_curves(subjvids);    
    
    
    ############ NOW WE SELECTED VIDEOS #############
    
    
    MINLOOKTIME_SEC=4;
    MIN_NSUBJ = 40;
    
    # Create binary matrix (subjects as rows, videos as columns)
    matrix = (subjvids.pivot(index='subj', columns='vid', values='goodsecs') > MINLOOKTIME_SEC).astype(int)
        
    # 2. Get the exact names/IDs of the top N most active subjects
    chosen_subjs = matrix.sum(axis=1).sort_values(ascending=False).index[:MIN_NSUBJ]
    
    # 3. Filter the matrix to only these subjects
    sub_subset = matrix.loc[chosen_subjs]
    
    # 4. Find videos watched >6s by ALL of these chosen subjects
    all_watched_mask = (sub_subset.sum(axis=0) == MIN_NSUBJ)
    chosen_vids = all_watched_mask[all_watched_mask].index.tolist()
    
    # Convert subjects to a list for easy viewing
    chosen_subjs = chosen_subjs.tolist()
    
    print(f"Keep these {len(chosen_subjs)} subjects: {chosen_subjs} (C: {len([c for c in chosen_subjs if c.startswith('C')])}  P: {len([c for c in chosen_subjs if c.startswith('P')])}\n")
    print(f"Keep these {len(chosen_vids)} videos: {chosen_vids}")
    
    final_subjvids = subjvids[ subjvids['subj'].isin(chosen_subjs) &
                               subjvids['vid'].isin(chosen_vids) ];

    goodkeys = final_subjvids['myidx'].tolist();
    print(len(goodkeys)); #REV: OK 1600 for 40x40
    
        
    ##### Given the subset of videos (and subjs), we will compute parameters and save
    ##### However, parameters will be coalesced "per-subject"
    ##### Ignoring actual videos...
    #####   For scanpath, should it be "union over all videos" (per unit time)?
    #####    Or, "mean of scanpath/time of each video"? THE FORMER!
    
    allresults=list();
    for subj, subjtrials in final_subjvids.groupby('subj'):
        myevents = evdf[ evdf['myidx'].isin(subjtrials['myidx']) ];
        mysamps = sadf[ sadf['myidx'].isin(subjtrials['myidx']) ];
        print("Got {} unique trials for subj {}".format(len(mysamps['myidx'].unique()), subj));

        totalwatch=final_subjvids['goodsecs'].sum();
        
        saccs = myevents[ myevents['label']=='SACC' ];
        blnks = myevents[ myevents['label']=='BLNK' ];
        isis = myevents[ myevents['label']=='ISI' ];

        MAXBLNK_SEC=0.500;
        
        blnks = blnks[ blnks['dursec'] < MAXBLNK_SEC ]; #REV: otherwise it's just missing data...

        BIGSMALL_CUTOFF=3
        
        myresult = dict(
            subj=subj,
            xmean=mysamps['cgx_dva'].mean(),
            ymean=mysamps['cgy_dva'].mean(),
            xstd=mysamps['cgx_dva'].std(),
            ystd=mysamps['cgx_dva'].std(),
            xyentropy=compute_kde_continuous_entropy(mysamps['cgx_dva'],
                                                     mysamps['cgy_dva'],
                                                     screen_width=12,
                                                     screen_height=12,
                                                     ),
            blnk_rate=len(blnks.index)/totalwatch, #REV: could be missing data? Should use pupilsize
            
            scanpathlen=saccs['ampldva'].sum(),
            
            sacc_rate=len(saccs.index)/totalwatch,
            sacc_ampl_med=saccs['ampldva'].median(),
            sacc_ampl_std=saccs['ampldva'].std(),
            
            sacc_bigsmall3dva_ratio=len(saccs[ saccs['ampldva'] > BIGSMALL_CUTOFF ].index) / len(saccs[ saccs['ampldva'] <= BIGSMALL_CUTOFF ].index),
            
            isi_dur_med=isis['dursec'].median(),
            isi_dur_std=isis['dursec'].std(),
                        
            #saccdur_med=saccs['ampldva'].median(),
            #REV: saliency etc.
            
        );
        allresults.append(myresult);
        pass;

    regressors=pd.DataFrame(allresults);
    regressors.to_csv('allregressors.csv', index=False);
    
    '''
    for key in goodkeys:
        mytrdf=trgrps.get_group(key);
        subj=mytrdf.iloc[0]['name'];
        vid=mytrdf.iloc[0]['video'];
        
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
        
        if( goodsecs > MINLOOKTIME_SEC ): #REV: how "much" of a trial do they need to "watch" lol.
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
        pass; #REV: end for each in groupby(mygrp);
    '''
    
    
    exit(0);


    
    
    
    
    
    
    

    
    valid_views = subjvids[subjvids['goodsecs'] >= MINLOOKTIME_SEC]
    videos_per_subject = valid_views.groupby('subj')['vid'].nunique()
    
    # 2. Define threshold (e.g., must watch at least 50% of all available videos)
    min_videos = len(vidstoview) * 0.80;
    good_subjects = videos_per_subject[videos_per_subject >= min_videos].reset_index(); #index
    
    print("GOOD SUBJS");
    print(good_subjects);
    print("JUST SUBJ COL");
    print(good_subjects.subj);
    print("N UNIQUE SUBJS (who seen >90% of videos)");
    print(len(good_subjects.subj.unique()));
    
    
    
    
    # 3. Filter the original dataframe
    df = subjvids[ subjvids['subj'].isin(good_subjects.subj) ]
    print(df);
    
    total_subs = df["subj"].nunique()
    
    # Filter videos watched > 6 seconds by all subjects
    valid_vids = df.groupby("vid").filter(
        lambda g: (g["goodsecs"] >= MINLOOKTIME_SEC).all() and (g["subj"].nunique() == total_subs)
    )["vid"].unique()
    
    print(valid_vids);
    exit(0);
    
    
    
    valid_views = subjvids[subjvids['goodsecs'] >= MINLOOKTIME_SEC]
    total_subjects = subjvids['subj'].nunique()
    print("Total {} subjs".format(total_subjects));
    video_counts = valid_views.groupby('vid')['subj'].nunique();
    print(video_counts);
    
    shared_videos = video_counts[video_counts == total_subjects].index.tolist()
    
    print("Vids seen by all subjs: ", shared_videos);
    exit(0);
    
    
    vids = subjvids.groupby('vid').filter(lambda x: (x['goodsecs'] >= MINLOOKTIME_SEC).all()).reset_index(drop=True)
    print(subjvids.subj.unique());
    print("GOOD vids:");
    print(vids);
    print("N GOOD", len(vids.index));
    
    subjvids = subjvids[ subjvids.vid.isin(vids) ];
    if( subjvids.goodsecs.min() < MINLOOKTIME_SEC ):
        raise Exception("WTF");
    else:
        print("Good");
    return 0;

if __name__=='__main__':
    exit(main());
    pass;
