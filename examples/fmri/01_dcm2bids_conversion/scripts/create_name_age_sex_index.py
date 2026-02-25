
import pandas as pd
import os
import sys
import re

import shutil
import os

def extract_archive(archive_path, extract_dir=None):
    """
    Extracts various archive formats (zip, tar, tar.gz, etc.) to a specified directory.
    
    Args:
        archive_path (str): The path to the archive file.
        extract_dir (str, optional): The target directory for extraction. 
                                     If None, the current working directory is used.
    """
    if extract_dir and not os.path.exists(extract_dir):
        os.makedirs(extract_dir)
        pass;
    
    try:
        shutil.unpack_archive(archive_path, extract_dir)
        print(f"Archive '{archive_path}' successfully extracted to '{extract_dir or os.getcwd()}'")
    except ValueError as e:
        print(f"Error extracting archive: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        pass;
    return;




dir=sys.argv[1];

mylst=list();
for d1 in os.listdir(dir):
    bn = os.path.basename(d1);
    print("Checking [{}] (bn={})".format(d1, bn));
    pattern="^(P|C)[0-9]{3}$"
    mymatch = re.match(pattern, bn);
    if( not mymatch ):
        print("---------- Not matched CXXX or PXXX");
        continue;
    
    print("Matched: ", mymatch.group(0));
    patientcontrol=mymatch.group(1);
    patientcontrol='patient' if patientcontrol=='P' else 'control';
    
    d2list2= os.listdir(os.path.join(dir,d1));
    d2list = [ d for d in d2list2 if os.path.isdir(os.path.join(dir,d1,d)) ];
    if(len(d2list) != 1):
        #raise Exception("Wtf has not just one file {} {}".format(d1, d2list));
        print("Whoa, originally not just 1?");
        if( len(d2list2) == 1 and
            os.path.isfile(os.path.join(dir,d1,d2list2[0]))
            ):
            print("But, found file: {}".format(d2list2[0]));
            extract_archive(os.path.join(dir,d1,d2list2[0]), os.path.join(dir,d1));
            pass;
        
        d2list2= os.listdir(os.path.join(dir,d1));
        #for d in d2list2:
        #    mypathx= os.path.join(dir,d1,d);
        #    print("Testing {}".format(mypathx));
        #    print("Is dir: {}  Is file: {}".format(os.path.isdir(mypathx), os.path.isfile(mypathx)));
        #    pass;
        
        d2list = [ d for d in d2list2 if True==os.path.isdir(os.path.join(dir,d1,d)) ];
        if(len(d2list) != 1):
            raise Exception("Wtf has not just one file {} {}  (FULL DIR: {})".format(d1, d2list, d2list2));
        pass;
        
    else:
        print("SUCCESS: found dir {}".format(d2list[0]));
        pass;
    
    
            

    mydir=os.path.basename(d2list[0]);
    print("MYDIR: ", mydir);
    pattern="([0-9]{8})_([0-9]{4})_([A-Z]{2})_([0-9]{3})Y_(F|M)"; #20230703_1209_MM_054Y_M
    smatch=re.match(pattern, mydir);
    if( smatch ):
        date=smatch.group(1);
        time=smatch.group(2);
        initials=smatch.group(3)
        age=int(smatch.group(4));
        sex=smatch.group(5);
        ndict=dict(participant_id="sub-{}".format(bn), date=date, time=time, initials=initials, age=age, sex=sex, group=patientcontrol);
        mylst.append(ndict);
        pass;
    else:
        raise Exception("WTF");
    
    pass;


df=pd.DataFrame(mylst);
print(df);
df.to_csv('name_age_sex_index.csv', index=False, sep='\t');
