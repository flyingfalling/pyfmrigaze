## #!/usr/local/fsl/bin python

##REV: this just reformats them from being bids::subj_ID/func/blah_BOLD.nii to
## func/blah_BOLD.nii   https://github.com/bids-standard/pybids/issues/950
import json
import argparse
import re
parser = argparse.ArgumentParser(
    prog = "remove_bidsuri",
    usage = "python remove_bidsuri.py <subj_id> <homedir>",
    description = "remove BIDS URI from IntendedFor in fmap file.",
    add_help = True,
)
parser.add_argument("subj_id", type=str, help="Subject ID, e.g. 012")
parser.add_argument("homedir", type=str, help="Home directory")
args = parser.parse_args()
## Main ##
subj_id = args.subj_id
homedir = args.homedir

#def remove_uri(json_label):
def remove_uri(fmapfile):
    #fmapfile = f'{homedir}/sub-{subj_id}/fmap/sub-{subj_id}_{json_label}.json'
    with open(fmapfile, "r") as fmap_json:
        data_json = json.load(fmap_json)
        pass;
    string_to_remove = f'bids::sub-{subj_id}/'
    re_str_to_rm = '^' + string_to_remove
    uri_exists = False
    for bold_file in data_json['IntendedFor']:
        if bool(re.match(re_str_to_rm, bold_file)):
            uri_exists = True
    if not uri_exists:
        #raise ValueError("No BIDS URI found.")
        print("No BIDS URIs found in {fmapfile}: (already formatted correctly). Returning.");
        return;
    
    removed_list = [i.removeprefix(string_to_remove) for i in data_json['IntendedFor']]
    data_json['IntendedFor'] = removed_list
    with open(fmapfile, "w") as fmap_json:
        json.dump(data_json, fmap_json, indent=4)
    print(f'BIDS URI was removed from {fmapfile}.')
    return;


mydir='{}/sub-{}/fmap/'.format(homedir, subj_id);
import os;

fmap_files=os.listdir(mydir);
for f in fmap_files:
    if( len(f)>5 and f[-5:].lower()=='.json' ):
        remove_uri( os.path.join(mydir, f) );
        pass;
    pass;
## sub-P020_dir-PA_run-01_epi.json
#remove_uri('dir-PA_epi')
#remove_uri('dir-AP_epi')
