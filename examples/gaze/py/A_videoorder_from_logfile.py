

# Starting EXPERIMENT: Subject name will be: P015_AF, tag FMRI starting 2024-11-14-11-26-12
# Lead rest! 2.9999990463256836 sec (requested 3.0)
# Doing for vid /home/scz7t/Desktop/fmri_lab90c2//B/clip_0000233399.mp4 (full duration 10.0 sec)
#VID BLOCK elapsed after leading rest 2.993206024169922 sec
# Doing DOVID, vidname: clip_0000233399.mp4
#Actual dovid took 10.008891105651855 sec
#VID Block 13.002177000045776/36.0 sec
#VID Block 1/3 Video
#Doing for vid /home/scz7t/Desktop/fmri_lab90c2//B/clip_0000239346.mp4 (full duration 10.0 sec)
#Doing DOVID, vidname: clip_0000239346.mp4

#Executing for key [3] (Video Task: FMRI7T_FIXED_PA)
#Will do up to block length 330.0 seconds, 30 vids, lead rest sec 15.0,   tail rest sec 15.0, btw vid sec: 0.0.
#Lead rest! 14.999997854232788 sec (requested 15.0)
#VID BLOCK elapsed after leading rest 14.98569107055664 sec


import re
import pandas as pd
from pathlib import Path

def parse_fmri_log(logfile): #file_content):
    file_content='';
    with open(logfile, "r") as f:
        file_content = f.read();
        pass;
    
    # 1. Initialize our storage and state trackers
    file_info = {'subject': None, 'date_time': None}
    blocks_data = []
    videos_data = []
    
    block_order_counter = 0
    
    # 2. Define all our regex patterns up front
    p_file = r"Subject name will be:\s*(?P<subject>[^,]+).*?starting\s*(?P<date_time>[\d-]+)"
    p_block_start = r"Executing for key \[\d+\]\s*\(Video Task:\s*(?P<task_name>[^)]+)\)"
    p_state = r"My state name is\s*(?P<state_name>\w+)"
    p_params = r"Will do up to block length\s*(?P<len>\d+\.?\d*).*?(?P<vids>\d+)\s*vids.*?lead rest sec\s*(?P<lead>\d+\.?\d*).*?tail rest sec\s*(?P<tail>\d+\.?\d*).*?btw vid sec:\s*(?P<btw>\d+\.?\d*)"
    p_lead_req = r"Lead rest!.*\(requested\s*(?P<req>[\d.]+)\)"
    p_lead_actual = r"VID BLOCK elapsed after leading rest\s*(?P<actual>[\d.]+)\s*sec"
    
    p_vid_path = r"Doing for vid\s+(?P<raw_path>[^\s]+)\s+\(full duration\s+(?P<duration>[\d.]+)\s*sec\)"
    p_vid_elapsed = r"VID Block\s+(?P<elapsed>[\d.]+)/(?P<total_time>[\d.]+)\s*sec"
    p_vid_index = r"VID Block\s+(?P<idx>\d+)/(?P<total_vids>\d+)\s*Video"
    
    p_tail = r"Doing tail-end rest.*?doing\s*(?P<actual>[\d.]+)\s*sec"
    p_block_end = r"Block elapsed:\s*(?P<elapsed>[\d.]+)\s*sec"

    # 3. Process line by line
    for line in file_content.splitlines():
        
        # --- FILE LEVEL ---
        if "Starting EXPERIMENT" in line:
            m = re.search(p_file, line)
            if m:
                file_info.update(m.groupdict())
                
        # --- BLOCK LEVEL ---
        elif "Executing for key" in line:
            m = re.search(p_block_start, line)
            if m:
                block_order_counter += 1
                # Start a new dictionary for this block and append it to our list
                current_block = {
                    'block_order': block_order_counter,
                    'task_name': m.group('task_name'),
                    'state_name': None, 'param_len': None, 'param_vids': None,
                    'lead_rest_req': None, 'lead_rest_actual': None, 'lead_rest_start': 0.0,
                    'tail_rest_actual': None, 'block_total_elapsed': None
                }
                blocks_data.append(current_block)

        # Update the CURRENT block if it exists
        elif blocks_data:
            if "My state name is" in line:
                m = re.search(p_state, line)
                if m: blocks_data[-1]['state_name'] = m.group('state_name')
                
            elif "Will do up to block length" in line:
                m = re.search(p_params, line)
                if m:
                    blocks_data[-1].update({
                        'param_len': float(m.group('len')),
                        'param_vids': int(m.group('vids')),
                        'param_lead': float(m.group('lead')),
                        'param_tail': float(m.group('tail')),
                        'param_btw': float(m.group('btw'))
                    })
                    
            elif "Lead rest!" in line:
                m = re.search(p_lead_req, line)
                if m: blocks_data[-1]['lead_rest_req'] = float(m.group('req'))
                
            elif "VID BLOCK elapsed after leading rest" in line:
                m = re.search(p_lead_actual, line)
                if m: blocks_data[-1]['lead_rest_actual'] = float(m.group('actual'))
                
            elif "Doing tail-end rest" in line:
                m = re.search(p_tail, line)
                if m: blocks_data[-1]['tail_rest_actual'] = float(m.group('actual'))
                
            elif "Block elapsed:" in line:
                m = re.search(p_block_end, line)
                if m: blocks_data[-1]['block_total_elapsed'] = float(m.group('elapsed'))

            # --- VIDEO TRIAL LEVEL ---
            elif "Doing for vid" in line:
                m = re.search(p_vid_path, line)
                if m:
                    file_path = Path(m.group('raw_path'))
                    # Start a new video dictionary
                    current_video = {
                        'block_order': block_order_counter, # Link back to parent block
                        'vid_name': file_path.name,
                        'vid_group': file_path.parent.name,
                        'vid_expected_duration': float(m.group('duration')),
                        'vid_elapsed_in_block': None,
                        'vid_index': None
                    }
                    videos_data.append(current_video)
                    
            # Update the CURRENT video if it exists
            elif videos_data and videos_data[-1]['block_order'] == block_order_counter:
                if "VID Block" in line and "sec" in line:
                    m = re.search(p_vid_elapsed, line)
                    if m: videos_data[-1]['vid_elapsed_in_block'] = float(m.group('elapsed'))
                        
                elif "VID Block" in line and "Video" in line:
                    m = re.search(p_vid_index, line)
                    if m: videos_data[-1]['vid_index'] = int(m.group('idx'))

    # 4. Convert lists to DataFrames
    df_blocks = pd.DataFrame(blocks_data)
    df_videos = pd.DataFrame(videos_data)

    df_blocks['logfile'] = logfile;
    
    # Optional: Filter blocks to only keep "FMRI7T_" tasks if needed
    # df_blocks = df_blocks[df_blocks['task_name'].str.startswith("FMRI7T_", na=False)]
    
    # 5. Merge into one large, tidy DataFrame based on the block order
    if not df_videos.empty and not df_blocks.empty:
        master_df = pd.merge(df_videos, df_blocks, on='block_order', how='outer')
        
        # Add the file-level info to every row
        master_df['subject'] = file_info['subject']
        master_df['date_time'] = file_info['date_time']

        return master_df
    else:
        return df_blocks # Returns just blocks if no videos were found

# --- Example Usage ---
# with open("experiment.log", "r") as f:
#     log_content = f.read()
# master_dataframe = parse_fmri_log(log_content)
# print(master_dataframe.head())



import argparse

def main():
    parser = argparse.ArgumentParser(description="Parse log files and save the extracted data.")

    # nargs='+' requires at least one file, but accepts multiple separated by spaces
    parser.add_argument(
        '-i', '--input', 
        nargs='+', 
        required=True, 
        help="Path to one or more input log files."
    )

    # required=True forces the user to provide this flag
    parser.add_argument(
        '-o', '--output', 
        required=True, 
        help="Path and name for the output file (e.g., final_data.csv)."
    )

    args = parser.parse_args()

    # --- Your script logic goes here ---
    print(f"Found {len(args.input)} input file(s) to process:")
    dflist=list();
    for logfile in args.input:
        print("Processing {}".format(logfile));
        
        df = parse_fmri_log(logfile); #log_content);
        dflist.append(df);
        pass;
    df = pd.concat(dflist).reset_index(drop=True);
    
    print(f"\nData will be saved to: {args.output}")
    df = df.dropna().reset_index(drop=True);
    df.to_csv(args.output, index=False);
    
    for (logfile, block), sdf in df.groupby(['logfile', 'block_order']):
        print(logfile, block);
        print(sdf.columns);
        print(sdf.vid_index);
        pass;
    
    return 0;

if __name__ == "__main__":
    exit(main());
    pass;
