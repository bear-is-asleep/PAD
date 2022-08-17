#!/sbnd/data/users/brindenc/.local/bin/python3.9
import sys
sys.path.append('/sbnd/data/users/brindenc/.local/lib/python3.9/site-packages')
sys.path.append('/sbnd/app/users/brindenc/mypython') #BC utils path
sys.path.append('.')
import PAD_config #Load vars (please configure this)
from bc_utils.utils import pic
from bc_utils.pmtutils import pic as pmtpic
import uproot
import numpy as np
import os

pic.print_stars()
print('Running make_pkls.py')

tree = uproot.open(PAD_config.uprootname)

#Constants
keys = tree.keys() #they have the same keys, don't worry
DATA_DIR = PAD_config.DATA_DIR #Where's your data going?
sample = PAD_config.sample #Sample name
fileID = PAD_config.fileID #file id
tlow = PAD_config.tlow #ms
thigh = PAD_config.thigh #ms
run_info_keys = ['run','subrun','event']

#Read events
readg4 = PAD_config.readg4
readop = PAD_config.readop
readcrt = PAD_config.readcrt
readmuon = PAD_config.readmuon

#Input sample name
#argList = sys.argv[1:]
#fileID = argList[0] #Able to overide file id with arglist

#Get g4 info
if readg4 and not os.path.exists(f'{DATA_DIR}/g4_df_{sample}__precut{fileID}.pkl') and PAD_config.remakedata:
  g4keys = PAD_config.g4keys 
  g4keys.extend(run_info_keys)
  g4_df = tree.arrays(g4keys,library='pd')
  g4 = g4_df.set_index(run_info_keys)

  #g4 first cuts for tracks
  g4.loc[:,'theta_yx'] = np.arctan2(g4.loc[:,'Py'],g4.loc[:,'Px']) #calculate angle using momentum
  temp = g4[g4.loc[:,'pathlen']>0] #Length it was in the detector for
  temp = temp[abs(temp.loc[:,'pdg']) == 13] #Muon
  temp = temp[temp.loc[:,'status'] == 1] #Primary particle
  g4_cut = temp.copy() #First cut

  #Treadout cuts 
  g4_cut = pmtpic.find_cosmicentrance(g4_cut) #find where cosmics enter detector, important for treadout
  g4_cut = pmtpic.get_treadout(g4_cut) #get treadout
  temp = g4_cut[g4_cut.loc[:,'treadout'] < thigh*1e6] #convert to ns
  temp = temp[temp.loc[:,'treadout'] > tlow*1e6] #convert to ns
  g4_df = temp.copy() #Second cut
  print(f'Making {DATA_DIR}/g4_df_{sample}__precut{fileID}.pkl')
  g4_df.to_pickle(f'{DATA_DIR}/g4_df_{sample}__precut{fileID}.pkl')

if readop and not os.path.exists(f'{DATA_DIR}/op_df_{sample}__precut{fileID}.pkl') and PAD_config.remakedata: #Needed for PAD, so please include this
  opkeys = [key for key in keys if 'op' in key]
  opkeys.extend(run_info_keys)
  opkeys.remove('nophits')

  op_df = tree.arrays(opkeys,library='pd')
  op_df = op_df.set_index(run_info_keys)
  #Add tpc info to op info
  op_df.loc[:,'op_tpc'] = op_df.loc[:,'ophit_opch'].values%2 #if the channel is odd, the tpc is 1, this works out nicely
  print(f'Making {DATA_DIR}/op_df_{sample}__precut{fileID}.pkl')
  op_df.to_pickle(f'{DATA_DIR}/op_df_{sample}__precut{fileID}.pkl')
  
if readcrt and not os.path.exists(f'{DATA_DIR}/crt_df_{sample}__precut{fileID}.pkl') and PAD_config.remakedata:
  crtkeys = [key for key in keys if 'crt' in key]
  crtkeys.extend(run_info_keys)
  crt_df = tree.arrays(crtkeys,library='pd')
  crt_df = crt_df.set_index(run_info_keys)
  print(f'Making {DATA_DIR}/crt_df_{sample}__precut{fileID}.pkl')
  crt_df.to_pickle(f'{DATA_DIR}/crt_df_{sample}__precut{fileID}.pkl')

if readmuon and not os.path.exists(f'{DATA_DIR}/muon_df_{sample}__precut{fileID}.pkl') and PAD_config.remakedata:
  muonkeys = [key for key in keys if 'muon' in key]
  muonkeys.extend(run_info_keys)
  muon_df = tree.arrays(muonkeys,library='pd')
  muon_df = muon_df.set_index(run_info_keys)
  print(f'Making {DATA_DIR}/muon_df_{sample}__precut{fileID}.pkl')
  muon_df.to_pickle(f'{DATA_DIR}/muon_df_{sample}__precut{fileID}.pkl')

pic.print_stars()