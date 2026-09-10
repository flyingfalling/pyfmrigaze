
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import seaborn as sns

import numpy as np
from scipy.stats import gaussian_kde, zscore

import peyeutils as pu;

import os;
import cv2;

def compute_saccade_direction_ratios(df, angle_col='angle'):
    """
    Computes horizontal and vertical saccade ratios from directional angles.
    Assumes angles are in degrees (e.g., 0 to 360, or -180 to 180).
    """
    # 1. Normalize all angles strictly to the [0, 360) degree range
    angles_360 = np.mod(df[angle_col].to_numpy(), 360)
    
    # 2. Count horizontal saccades (0°/360° is East/Right, 180° is West/Left)
    # Horizontal cones: [-45°, +45°] (315° to 360° AND 0° to 45°) and [135°, 225°]
    is_horizontal = ((angles_360 >= 315) | (angles_360 <= 45)) | ((angles_360 >= 135) & (angles_360 <= 225));
    
    # 3. Count vertical saccades (90° is North/Up, 270° is South/Down)
    # Vertical cones: [45°, 135°] and [225°, 315°]
    is_vertical = ((angles_360 > 45) & (angles_360 < 135)) | ((angles_360 > 225) & (angles_360 < 315))
    
    total_saccades = len(angles_360)
    if total_saccades == 0:
        return {'horizontal_ratio': 0.0, 'vertical_ratio': 0.0}
    
    # 4. Calculate relative feature ratios (perfect for ML regressors)
    features = {
        'horizontal_ratio': np.sum(is_horizontal) / total_saccades,
        'vertical_ratio': np.sum(is_vertical) / total_saccades
    }
    
    return features;


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


#REV: use probability density (i.e. use ptsinbin/(ntotalpts*imgwid*imghei) instead of just ptsinbin/ntotalpts).
##   I.e. scale by 1/(npixels) i.e.   1/(wid*hei).
#REV: are there any points outside of xmin/xmax
def points2d_to_pdensity2d(x_coords, y_coords,
                           xmin, xmax,
                           ymin, ymax,
                           nxbins, nybins):
    import numpy as np;
    
    hist, y_edges, x_edges = np.histogram2d(
        y_coords, 
        x_coords, 
        bins=[nybins, nxbins],
        range=[[ymin, ymax], [xmin, xmax]]
    );
    
    total_points = np.sum(hist); #number of points used to generate it (divide by this to ensure sum to 1)
    prob_matrix = hist / (total_points if total_points > 0 else 1.0);
    my_image = np.ones((nybins, nxbins), dtype=np.float64);  # Placeholder image
    faded_image = my_image * prob_matrix
    
    #REV; smooth it...?
    return prob_matrix, hist.astype(int);



# 6. Example: Multiply it element-wise by a grayscale image

#REV: shit I need to know size of video and convert to video coordinates (zero-centered and zeroed normally).

#REV: viddf and saldf should contain info about where video (files) are located, samprate, etc.
#REV: I guess we should have "flip" timing too but meh.
#REV: saldf, likewise (just get video's salmap based on name and etc.).
#REV: in DF, it has the salmap files and their types (lum, ori, etc.)? Or we just have a list.

#REV: we could just have an open videoreader?
#REV: hard-code a function get video name and salfile names. And extract information from there
## (assume e.g. framerate is identical to when it was shown to subject).
def compute_persubjvid_regressors(subj,
                                  mytrials,
                                  mysamps,
                                  myevents,
                                  myedfs,
                                  viddir,
                                  saldir):
    
    print(" PER VIDEO PER SUBJ: Subj={}".format(subj));

    salresults=list();
    
    #REV: theoretically, each person should have seen each video only once! 
    for myvid, subtrdf in mytrials.groupby('video'):
        myidx = subtrdf.iloc[0]['myidx'] ;
        
        if(len(subtrdf.index) != 1):
            print(subtrdf);
            raise Exception("Video {} has not just one trial!".format(myvid));
        
        myedffile = subtrdf['edffile'].unique();
        if( len(myedffile) != 1 ):
            raise Exception("Wtf more than one or not one EDF file? {}".format(myedffile));

        myedffile=myedffile[0];
        myedf = myedfs[ myedfs['edffile'] == myedffile ];
        if( len(myedf.index) != 1 ):
            raise Exception("Wtf edffile CSV has more than one row with identically named EDF file? -- REV: maybe separate by e.g. path? {}".format(myedf));
        
        
        myedf = myedf[
            [
                'recinfo_EYE_USED_mode',
                'recinfo_SCREEN_WPX',
                'recinfo_SCREEN_HPX',
                'recinfo_SCREEN_BGRGB',
                'recinfo_VB_CX',
                'recinfo_VB_CY',
                'recinfo_VB_WPX',
                'recinfo_VB_HPX',
                'recinfo_VB_DM',
                'recinfo_VB_PPM',
                'recinfo_VB_TARGPX',
                'recinfo_VB_TARGDVA',
                'recinfo_VB_TARGM',
            ]
        ];
        
        #REV: just take the first (and only) row, i.e. return a dict or record (sequence? series?) or whatever.
        recparams = myedf.iloc[0].to_dict();
        vidparams = subtrdf.iloc[0].to_dict();
        print("MY VIDPARAMS: ", vidparams);
        vidw = int(vidparams['vidw_px']);
        vidh = int(vidparams['vidh_px']);

        vidw_m = vidparams['vidw_px'] / recparams['recinfo_VB_PPM'];
        vidh_m = vidparams['vidh_px'] / recparams['recinfo_VB_PPM'];
        
        vidwdva = np.degrees(np.arctan2(vidw_m/2, recparams['recinfo_VB_DM'] ) );
        vidwdva *= 2; #REV: because was half, centered triangle.
        dvapm = pu.utils.get_center_dva_per_meter( recparams['recinfo_VB_DM'] , recparams['recinfo_VB_PPM']);
        dvappx = dvapm / recparams['recinfo_VB_PPM'];
        vidhdva = np.degrees(np.arctan2(vidh_m/2, recparams['recinfo_VB_DM'] ) );
        vidhdva *= 2; #REV: because was half, centered triangle.

        print("Video {} for subj={} is shown at {} x {} dva".format(myvid, subj, vidwdva, vidhdva));
        print("(NAIVE: ) {} x {} dva".format(dvapm*vidw_m, dvapm*vidh_m));
        
        #  start_s,end_s,video,vidw_px,vidh_px,vidxpos_px,vidypos_px,fmrist_s,fmri_offset_s,trialidx,blkidx,grp,
        ##  APPA,ispract,rest,blkstart_s,blkend_s,name,edfdatetime,edffile


        #REV: OK now do actual computation and make videos etc.
        #REV: note I should make "manysubj" video (after the fact). This is for saliency though.
        #REV: I could make huge T*X*Y matrix (T timepoints, X wid, Y hei), and multiply by
        #REV: a mask thing (T*X*Y) which represents the positive and negative samples.
        #REV: then sum within timepoints (T) and take percentile of positives in negatives.

        #REV: easier to do for all frames? Or for all gaze points (assuming 1/frame)?

        
        vidsamps = mysamps[ mysamps['myidx'] == subtrdf.iloc[0]['myidx'] ].copy();
        priorsamps = mysamps[ mysamps['video'] != myvid ].copy();
        
        
        vidsamps['x'] = vidsamps['cgx_px'] + vidw/2;
        vidsamps['y'] = vidsamps['cgy_px'] + vidh/2;
        vidsamps['y'] = vidh - vidsamps['y']; #REV; for opencv, top is 0.
        
        #print(vidsamps['cgx_px'].median());
        #print(vidsamps['cgy_px'].median());

        #REV: stupid to do this each time, but vidw/vidh may change each time.
        #REV: although, vid size of originals may change too but whatever...
        priorsamps['x'] = priorsamps['cgx_px'] + vidw/2;
        priorsamps['y'] = priorsamps['cgy_px'] + vidh/2;
        priorsamps['y'] = vidh - priorsamps['y']; #REV; for opencv, top is 0.
        
        priorprobs2d, priorhist = points2d_to_pdensity2d(priorsamps['x'],
                                                         priorsamps['y'],
                                                         0, vidw,
                                                         0, vidh,
                                                         vidw,
                                                         vidh
                                                         );
        
        #print(priorhist.dtype);
        #print(priorhist);
        
        
        if( len(vidsamps.eye.unique()) != 1 ):
            raise Exception("more than one eye's data in samples, you need to subset (maybe)");
        
        print("Got {} timepoints ({}-{})".format(len(vidsamps), vidsamps['Tsec'].min(), vidsamps['Tsec'].max()));
        
        ## REV: need access to video information. I.e. samplerate, time of each frame, etc.
        ## REV: get "OG" video (for making pretty videos) and saliency videos too.

        #REV: subj_vid_trial_gaze.mp4
        
        
        vidpath=os.path.join(viddir, vidparams['grp'], myvid); #blah/A/clip_XXXX.mpg
        
        cap, framedf, capparams = pu.utils.read_video_timestamps(vidpath, timename='Tsec');
        
        fourcc = cv2.VideoWriter_fourcc(*"mp4v");
        outw = int(capparams['wpx'])//4;
        outh = int(capparams['hpx'])//4;
        
        vw = cv2.VideoWriter('{}_{}.mkv'.format(subj, myvid),
                             fourcc,
                             capparams['fps'],
                             (outw, outh) );


        ####### PARAMETERS FOR SALIENCY MODELS ETC ############
        salblur_dva_radius= 0.33; #REV: size is only 10-12 deg video size...
        #REV: this is more to account for eyetracker.
        salblur_px_radius = salblur_dva_radius / dvappx;
        print("Blurring sal radius={:3.1f}dva (={:3.1f} px)".format(salblur_dva_radius, salblur_px_radius));
        
        before_time_sec= 0.0; #0;
        after_time_sec = 0.250; #300; #0;
        
        salkinds=['ori', 'col', 'lum', 'mot', 'fin'];
        
        ######### END PARAMETERS #############################
        
        dt = 1/capparams['fps'];
        vidsamps['Tsec'] = vidsamps['Tsec'] - vidparams['start_s'];

        #REV: I should zero-out blinks and saccades etc.?
        
        #salkinds=['ori', 'col', 'lum', 'mot', 'fli', 'fin'];

        ########## OPTIONS ##################

        MKVID=False; #True; #False;
        
        ############ END OPTIONS ############
        

        spctls=dict();
        svws = dict();
        if( saldir ):
            salcaps = dict();
            
            for k in salkinds:
                spctls[k]=0;
                salpath=os.path.join(saldir, vidparams['grp'], myvid); #blah/A/clip_XXXX.mpg
                salpath += '_{}.mkv'.format(k);
                salcaps[k], framedf, capparams = pu.utils.read_video_timestamps(salpath, timename='Tsec');

                if(MKVID):
                    svws[k] = cv2.VideoWriter('{}_{}_{}.mkv'.format(subj, myvid, k),
                                              fourcc,
                                              capparams['fps'],
                                              (outw, outh) );
                    pass;
                pass;
            pass;
        
        nsamps=0;
        for i, row in framedf.iterrows():
            if( i % 30 == 0 ):
                print("{}/{} frames".format(i, len(framedf.index)));
                pass;
            vidt = row['Tsec'];
            #print(vidparams['start_s']);
            #print(vidparams['blkstart_s']);
            #print(vidparams['fmri_offset_s']);
            #print(vidparams['fmrist_s']);
            #print(vidsamps["Tsec"]);
            
            #REV: to only get gaze samples inside this frame, use 0.
            #REV: this effectively "blurs" it a bit in time as well...
            #REV: note too high "before" will capture "predictive" looking, which our simple
            #REV: saliency model should NOT predict!!!!!
            tsamps = vidsamps[ (vidsamps['Tsec']>=(vidt+before_time_sec)) & (vidsamps['Tsec']<(vidt+dt+after_time_sec)) ];
            
            #print("For t={}-{}".format(vidt, vidt+dt));
            #print(tsamps);
            ret, frame = cap.read();
            if( False == ret ):
                raise Exception("Expecting more frames but there are none?");
            
            sframes=dict();
            pretty_sframes=dict();
            
            prior_sals=dict();
            poste_sals=dict();
            if( saldir ):
                for k in salkinds:
                    sret, sframes[k] = salcaps[k].read();
                    if( not sret ):
                        raise Exception("No more frames in {}".format(k));
                    sframes[k] = sframes[k][:,:,0]; #REV; it's 3 monochrome chan, just take first.
                    sframes[k] = cv2.resize(sframes[k], (vidw, vidh));

                    #REV: blur them (if needed)

                    if(MKVID):
                        pretty_sframes[k] = cv2.applyColorMap(sframes[k], cv2.COLORMAP_JET);
                        pass;
                    
                    
                    sframes[k] = cv2.GaussianBlur(sframes[k], (0,0), sigmaX=salblur_px_radius);


                    #REV: this is sampling 
                    prior_sals[k] = np.repeat(sframes[k].flatten(), priorhist.flatten());
                    img_sals[k] = sframes[k].flatten();
                    pass;
                pass;
            
            frame = cv2.resize( frame, (vidw, vidh) );
            gazex = tsamps['x']; #tsamps['cgx_px'] + vidw/2;
            gazey = tsamps['y'];

            
            
            #REV: Sample at each TP and FP position. I can't just multiply histogram * salmap,
            #REV: because I don't know if density came from high saliency and single sample, or
            #REV: because it came from low saliency and many samples...
            
            for x,y in zip(gazex, gazey):
                if( not np.isfinite(x) ):
                    continue;
                #print('{}/{}, {}/{}'.format(int(x),vidw,int(y),vidh));
                if(MKVID):
                    cv2.circle(img=frame,
                               center=(int(x),int(y)),
                               radius=7,
                               color=(0,0,255),
                               thickness=2,
                               lineType=cv2.LINE_AA,
                               );
                    pass;
                
                if( saldir ):
                    nsamps+=1;
                    for k in salkinds:
                        if(MKVID):
                            cv2.circle(img=pretty_sframes[k],
                                       center=(int(x),int(y)),
                                       radius=7,
                                       color=(0,0,255),
                                       thickness=2,
                                       lineType=cv2.LINE_AA,
                                       );
                            pass;
                        
                        if( y >=0 and y<vidh and x >=0 and x<vidw ):
                            poste_sals[k] = sframes[k][int(y),int(x)];

                            #REV: I could normalize each one to have same "weight"
                            #REV: then sum them all, and plot "gazed location" and "ungazed loc"
                            prior_pctl = (prior_sals[k] < poste_sals[k]).mean() * 100;
                            spctls[k]+=prior_pctl;
                            prior_nss = ( poste_sals[k] - np.mean(prior_sals[k]) ) / np.std(prior_sals[k]);
                            snsss[k]+= prior_nss;
                            
                            img_pctl = (img_sals[k] < poste_sals[k]).mean() * 100;
                            ipctls[k]+=img_pctl;
                            img_nss = ( poste_sals[k] - np.mean(img_sals[k]) ) / np.std(img_sals[k]);

                            #REV: information gain? (IG)
                            # IG = log2( p_model(x) / p_null(x) )
                            #print("Saliency ({}): ({},{}),val={:3.1f} = {:3.1f} pct".format(k, int(x), int(y), poste_sals[k], pctl));
                            pass;
                        else:
                            #print("({},{}) outside vid ({}x{}".format(int(x),int(y),vidw,vidh));
                            pass;
                        pass;
                    pass;
                pass;
            
            frame = cv2.resize(frame, (outw, outh));

            if( saldir  and   MKVID ):
                for k in salkinds:
                    pretty_sframes[k] = cv2.resize(pretty_sframes[k], (outw, outh));
                    svws[k].write(pretty_sframes[k]);
                    pass;
                pass;
            
            if(MKVID):
                vw.write(frame);
                pass;
            pass;
        
        cap.release();
        
        if(MKVID):
            vw.release();
            pass;
        
        if (saldir):
            for k in salkinds:
                salcaps[k].release();
                if(MKVID):
                    svws[k].release();
                    pass;
                pass;
            pass;

        if(saldir):
            for k in salkinds:
                pctl=spctls[k]/nsamps;
                salresults.append( dict(subj=subj, salkind=k, pctl=pctl, vid=myvid, myidx=myidx) );
                print("Sal ({}): {:3.1f} pctl".format(k, spctls[k]/nsamps));
                pass;
            pass;
        
        pass; #REV: end this video (trial) of this subject.

    subjdf=pd.DataFrame(salresults);
    print(subjdf);
    
    
    #REV: I can use cgx_px and cgy_px.
    #REV: However, for blurring etc., I should know how big the stimuli are. One method is simply divide the mean dva pos divided by mean px pos.
    #REV: that is a waste though. Better if something is passed through (dva/pix etc.?). But that is "mean". Better to have the ability to
    #REV: convert it again from first principles... Info is stored in...edftrials?
    
    '''
    for myvid, myvidsamps in mysamps.groupby('video'):
        #REV: prior distr is prior distribution of subjects (on vid!=v) for v in vids. Could just use all prior for large video set...
        #REV: but will be heavily biased for videos they watched more/longer.
        
        
        #REV: get "video time" of that stamp, get corresponding video frame (and saliency maps), get saliency of (around) gazed point
        #  Also, for +/- 500 msec, also for AUROC against prior distribution. Also for NSS against prior, against only this salmap,
        #  Also get information added.
        pass;
    '''
    
    return subjdf;


def compute_persubj_regressors(subj, mysamps, myevents, final_subjvids):
    totalwatch=final_subjvids['goodsecs'].sum();
    
    saccs = myevents[ myevents['label']=='SACC' ];
    blnks = myevents[ myevents['label']=='BLNK' ];
    isis = myevents[ myevents['label']=='ISI' ];
    
    MAXBLNK_SEC=0.500;
    
    blnks = blnks[ blnks['dursec'] < MAXBLNK_SEC ]; #REV: otherwise it's just missing data...

    BIGSMALL_CUTOFF=3
    dcenter=np.sqrt( (mysamps['cgx_dva']-mysamps['cgx_dva'].mean())**2 +
                     (mysamps['cgy_dva']-mysamps['cgy_dva'].mean())**2 );

    saccdirs = compute_saccade_direction_ratios(saccs);
    
    
    
    #REV: TODO
    # BCEA (pursuit/fixation jitter, and within-ISI pathlength, i.e. sum derivative?)
    # Fatigue (change in parameters for "later" trials in session/day versus "earlier").
    # Saliency value at target (zscore, i.e. NSE);
    mysamps['pa_z'] = zscore(mysamps['pa_lpf'], nan_policy='omit');
    myresult = dict(
        subj=subj,
        #xmean=mysamps['cgx_dva'].mean(),
        #ymean=mysamps['cgy_dva'].mean(),
        #xstd=mysamps['cgx_dva'].std(),
        #ystd=mysamps['cgx_dva'].std(),
        horiz_look_bias=mysamps['cgx_dva'].std()/mysamps['cgy_dva'].std(),
        mean_dist_baryxy=dcenter.mean(),
        pupilarea_zderiv=abs(mysamps['pa_z'].diff()).mean(),
        xyentropy=compute_kde_continuous_entropy(mysamps['cgx_dva'],
                                                 mysamps['cgy_dva'],
                                                 screen_width=10,
                                                 screen_height=10,
                                                 ),
        blnk_rate=len(blnks.index)/totalwatch, #REV: could be missing data? Should use pupilsize
        centerbias1_0dva=np.mean(dcenter<1),
        centerbias2_5dva=np.mean(dcenter<2.5),
        scanpath_persec=saccs['ampldva'].sum()/totalwatch,
        sacc_ampldur_mean=(saccs['ampldva']/saccs['dursec']).mean(), #REV: should fit a line? this will be biased by clustery values...not penalized by distance^2.
        sacc_rate=len(saccs.index)/totalwatch,
        sacc_ampl_med=saccs['ampldva'].median(),
        sacc_ampl_std=saccs['ampldva'].std(),
        #sacc_vert_ratio=saccdirs['vertical_ratio'],
        sacc_horiz_bias=saccdirs['horizontal_ratio'],

        sacc_smallbig1dva_ratio=len(saccs[ saccs['ampldva'] <= 1 ].index) / len(saccs[ saccs['ampldva'] > 1].index),

        sacc_smallbig3dva_ratio=len(saccs[ saccs['ampldva'] <= 3 ].index) / len(saccs[ saccs['ampldva'] > 3 ].index),

        #sacc_smallbig5dva_ratio=len(saccs[ saccs['ampldva'] <= 5 ].index) / len(saccs[ saccs['ampldva'] > 5 ].index),

        isi_dur_med=isis['dursec'].median(),
        isi_dur_std=isis['dursec'].std(),
        isi_vel_med=isis['avgvel'].median(),
        isi_vel_std=isis['avgvel'].std(), #REV: only fix or only pursuit, or mix of both?
        #isi_vel_med=isis['medvel'].median(),

        #saccdur_med=saccs['ampldva'].median(),
        #REV: saliency etc.

    );
    
    return myresult;



def main():
    trialscsv=sys.argv[1];
    eventscsv=sys.argv[2];
    samplscsv=sys.argv[3];
    
    recedfcsv = sys.argv[4];
    viddir = '/mnt/coishare/data/stimuli/fmri7T_vids_20221109' #'/mnt/coishare/data/stimuli/fmri_lab90c2/';
    saldir = viddir + '_salmaps';
    
    '''
    if( len(sys.argv) > 4 ):
        minviewsecs=float(sys.argv[4]);
        minviewsubjs=int(sys.argv[5]);
        pass;
    '''
    
    minviewsecs=-1;
    minviewsubjs=-1;

    
    trdf = pd.read_csv(trialscsv);
    evdf = pd.read_csv(eventscsv);
    sadf = pd.read_csv(samplscsv);

    recdf = pd.read_csv(recedfcsv);
    
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
        edffile = mytrdf.iloc[0]['edffile'];
        grp = mytrdf.iloc[0]['grp'];
        
        
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

        #REV: append other stuff such as edffile etc., which went into myidx?
        subjvids.append( dict(subj=subj, vid=vid, goodsecs=goodsecs, myidx=myidx, edffile=edffile, grp=grp) );
        
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
    
    #MINLOOKTIME_SEC=4;
    #MIN_NSUBJ = 40;

    #minviewsecs_todo=range(3, 6, 1);
    #minviewsubjs_todo=range(35, 51, 5);
    mins_todo=list();
    for a in range(35, 56, 10):
        mins_todo.append((3, a));
        pass;
    
    for a in range(35, 51, 5):
        mins_todo.append((4, a));
        pass;
    
    for a in range(35, 46, 5):
        mins_todo.append((5, a));
        pass;
    
    #for a in range(30, 36, 5):
    #    mins_todo.append(6, a);
    #    pass;
    
        
    if( minviewsecs >= 0 and
        minviewsubjs >= 0):
        print("Doing for single pair of MINVIEWSEC / MINVIEWSUBJ");
        minviewsecs_todo=[minviewsecs,];
        minviewsubjs_todo=[minviewsubjs,];
        pass;
    
    all_regressors=list();
    all_salresults=list();
    for minviewsecs, minviewsubjs in mins_todo:
        if(True): #REV: skip level for indent.            
            # Create binary matrix (subjects as rows, videos as columns)
            matrix = (subjvids.pivot(index='subj', columns='vid', values='goodsecs') > minviewsecs).astype(int)
            
            # 2. Get the exact names/IDs of the top N most active subjects
            chosen_subjs = matrix.sum(axis=1).sort_values(ascending=False).index[:minviewsubjs]
            
            # 3. Filter the matrix to only these subjects
            sub_subset = matrix.loc[chosen_subjs]
            
            # 4. Find videos watched >6s by ALL of these chosen subjects
            all_watched_mask = (sub_subset.sum(axis=0) == minviewsubjs)
            chosen_vids = all_watched_mask[all_watched_mask].index.tolist()
            minviewvids=len(chosen_vids);
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

            salresults=list();
            allresults=list();
            #REV: for each SUBJECT within this video subset context (i.e. shared videos of which each subject has seen >X sec of each)
            
            for subj, subjtrials in final_subjvids.groupby('subj'):
                myevents = evdf[ evdf['myidx'].isin(subjtrials['myidx']) ].copy();
                mysamps = sadf[ sadf['myidx'].isin(subjtrials['myidx']) ].copy();
                mytrs = trdf[ trdf['myidx'].isin(subjtrials['myidx']) ].copy();
                
                myedfs = recdf[ recdf['edffile'].isin(subjtrials['edffile']) ].copy();
                
                
                print("Got {} unique trials for subj {} (minviews: {},{})".format(len(mysamps['myidx'].unique()),
                                                                                  subj,
                                                                                  minviewsecs,
                                                                                  minviewsubjs));
                
                
                print("----- COMPUTING *PER VIDEO* REGRESSORS ------");
                persubjvid_results = compute_persubjvid_regressors(subj=subj, mytrials=mytrs, mysamps=mysamps, myevents=myevents, myedfs=myedfs, viddir=viddir, saldir=saldir);
                
                salresults.append(persubjvid_results);
                print("SUBJ {}, PCTL MEANS:".format(subj));
                print(persubjvid_results.groupby('salkind').mean(numeric_only=True));
                print("----- COMPUTING *PER SUBJECT* REGRESSORS ------");
                persubj_results = compute_persubj_regressors(subj=subj, mysamps=mysamps, myevents=myevents, final_subjvids=final_subjvids);
                
                
                allresults.append(persubj_results);
                pass;
            
            allsalresults = pd.concat(salresults);
            allsalresults['minviewsecs']=minviewsecs;
            allsalresults['minviewsubjs']=minviewsubjs;
            allsalresults['minviewvids']=minviewvids;
            
            regressors=pd.DataFrame(allresults);
            regressors['minviewsecs']=minviewsecs;
            regressors['minviewsubjs']=minviewsubjs;
            regressors['minviewvids']=minviewvids;
            all_regressors.append(regressors);
            all_salresults.append(allsalresults);
            pass;
        pass;
    #regressors.to_csv('allregressors_minsec_{}_minsubj_{}.csv'.format(minviewsecs,minviewsubjs), index=False);

    all_salresults = pd.concat(all_salresults, ignore_index=True);
    all_salresults.to_csv('allsalresults.csv', index=False);
    
    all_regressors = pd.concat(all_regressors, ignore_index=True);
    all_regressors.to_csv('allregressors.csv', index=False);
    
    
    return 0;

if __name__=='__main__':
    exit(main());
    pass;
