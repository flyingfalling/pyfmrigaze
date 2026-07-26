import pandas as pd
import sys
import os

csvdir=sys.argv[1];

allcsvs=os.listdir(csvdir);

samps = [ f.removesuffix('.samples.csv') for f in allcsvs if f.endswith('.samples.csv') ];
ev2 = [ f.removesuffix('.events2.csv') for f in allcsvs if f.endswith('.events2.csv') ];

samps = set(sorted(samps));
ev2 = set(sorted(ev2));

print(samps-ev2);
print(len(samps-ev2));

