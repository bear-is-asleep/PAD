#!/sbnd/data/users/brindenc/.local/bin/python3.9
import sys
from os import system
import os
sys.path.append('.')
import PAD_config

#Set python paths
cwd = os.getcwd()
system(f'source {cwd}/setup_PAD.sh')

mode = PAD_config.mode
remakedata = PAD_config.remakedata

if mode == 'PAD':
  system('./scripts/PAD.py')
elif mode == 'build':
  if remakedata:
    system('./scripts/make_pkls.py')
    system('./scripts/cut_tracks.py')
    system('./scripts/sum_PE.py')
elif mode == 'both': #No mode specified, do both
  if remakedata:
    system('./scripts/make_pkls.py')
    system('./scripts/cut_tracks.py')
    system('./scripts/sum_PE.py')
  system('./scripts/PAD.py')
  

