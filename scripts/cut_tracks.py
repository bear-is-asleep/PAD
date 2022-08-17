#!/sbnd/data/users/brindenc/.local/bin/python3.9
"""
Brinden Carlson
5/2/22

Make cuts based on muon tracks
"""

import sys
import os
sys.path.append('/sbnd/data/users/brindenc/.local/lib/python3.9/site-packages')
sys.path.append('/sbnd/app/users/brindenc/mypython') #My utils path
sys.path.append('.')
from bc_utils.utils import pic
import PAD_config
import pandas as pd
from time import time

pic.print_stars()
print('Running cut_tracks.py')

#File info
DATA_DIR = PAD_config.DATA_DIR #Where's your data going?
sample = PAD_config.sample #Sample name
fileID = PAD_config.fileID #file id

#Read events
readg4 = PAD_config.readg4
readop = PAD_config.readop
readcrt = PAD_config.readcrt
readmuon = PAD_config.readmuon

#Initialize list of dataframes
op_dfs = []
muon_dfs = []
crt_dfs = []
g4_dfs = []

#Define cuts here
def muon_track_cuts(fileid):
  global op_dfs
  global muon_dfs
  global crt_dfs
  global g4_dfs

  #Set to none to prepare for null values
  muon_df = None
  op_df = None
  crt_df = None
  g4_df = None


  ind_list = [] #Check if event exists in all dataframes
  indeces_keep = [] #Indeces to keep based on cuts
  if readmuon:
    muon_df = pd.read_pickle(f'{DATA_DIR}/muon_df_{sample}__precut{fileid}.pkl')
    muon_inds = list(muon_df.index.drop_duplicates().values)
    ind_list.append(muon_inds)
  if readop:
    op_df = pd.read_pickle(f'{DATA_DIR}/op_df_{sample}__precut{fileid}.pkl')
    op_inds = list(op_df.index.drop_duplicates().values)
    ind_list.append(op_inds)
  if readcrt:
    crt_df = pd.read_pickle(f'{DATA_DIR}/crt_df_{sample}__precut{fileid}.pkl')
    crt_inds = list(crt_df.index.drop_duplicates().values)
    ind_list.append(crt_inds)
  if readg4:
    g4_df = pd.read_pickle(f'{DATA_DIR}/g4_df_{sample}__precut{fileid}.pkl')
    g4_inds = list(g4_df.index.drop_duplicates().values)
    ind_list.append(g4_inds)

  #Check event info
  for row,line in muon_df.iterrows(): #Make cuts based on muon df - this will break if there's no 
    check1 = False #Good muon track check
    check2 = True #Event exists in all dataframes
    if round(line['muontrk_x1'],0) != round(line['muontrk_x2'],0): #Drop rows with matching x1 and x2 (check nearest 1st digit, python has rounding issues)
      check1 = True
    for ind in ind_list:
      if row not in ind:
        check2 = False
    if check1 and check2:
      indeces_keep.append(row) #We keep these

    #if abs(line['muontrk_x1']) < apa_threshold or abs(line['muontrk_x2']) < apa_threshold: #Keep near-apa muons 
    #  indeces_drop.append(row)
    #if row in op_inds and row in crt_inds and row in g4_inds:
    #  indeces_keep.append(row)
    #if line['nmuontrks'] > 1: #Only one track
    #  indeces_drop.append(row)
  indeces_keep = list(set(indeces_keep)) #Drop duplicate events

  if readop:
    op_dfs.append(op_df.loc[indeces_keep]) #Append good events to list
  if readmuon:
    muon_dfs.append(muon_df.loc[indeces_keep]) #Append good events to list
  if readcrt:
    crt_dfs.append(crt_df.loc[indeces_keep]) #Append good events to list
  if readg4:
    g4_dfs.append(g4_df.loc[indeces_keep]) #Append good events to list

def no_cuts(fileid):
  global op_dfs
  global muon_dfs
  global crt_dfs
  global g4_dfs

  #Set to none to prepare for null values
  muon_df = None
  op_df = None
  crt_df = None
  g4_df = None

  ind_list = [] #Check if event exists in all dataframes
  indeces_keep = [] #Indeces to keep based on cuts
  if readmuon:
    muon_df = pd.read_pickle(f'{DATA_DIR}/muon_df_{sample}__precut{fileid}.pkl')
    muon_inds = list(muon_df.index.drop_duplicates().values)
    ind_list.append(muon_inds)
  if readop:
    op_df = pd.read_pickle(f'{DATA_DIR}/op_df_{sample}__precut{fileid}.pkl')
    op_inds = list(op_df.index.drop_duplicates().values)
    ind_list.append(op_inds)
  if readcrt:
    crt_df = pd.read_pickle(f'{DATA_DIR}/crt_df_{sample}__precut{fileid}.pkl')
    crt_inds = list(crt_df.index.drop_duplicates().values)
    ind_list.append(crt_inds)
  if readg4:
    g4_df = pd.read_pickle(f'{DATA_DIR}/g4_df_{sample}__precut{fileid}.pkl')
    g4_inds = list(g4_df.index.drop_duplicates().values)
    ind_list.append(g4_inds)

  for row in op_inds:
    check = True #See if event exists in all dataframes
    for ind in ind_list:
      if row not in ind:
        check = False
    if check:
      indeces_keep.append(row)

  if readop:
    op_dfs.append(op_df.loc[indeces_keep]) #Append good events to list
  if readmuon:
    muon_dfs.append(muon_df.loc[indeces_keep]) #Append good events to list
  if readcrt:
    crt_dfs.append(crt_df.loc[indeces_keep]) #Append good events to list
  if readg4:
    g4_dfs.append(g4_df.loc[indeces_keep]) #Append good events to list


start = time()
#Check if files exist and if it should exist!
if readmuon:
  assert(os.path.exists(f'{DATA_DIR}/muon_df_{sample}__precut{fileID}.pkl'))
if readop:
  assert(os.path.exists(f'{DATA_DIR}/op_df_{sample}__precut{fileID}.pkl'))
if readg4:
  assert(os.path.exists(f'{DATA_DIR}/g4_df_{sample}__precut{fileID}.pkl'))
if readcrt:
  assert(os.path.exists(f'{DATA_DIR}/crt_df_{sample}__precut{fileID}.pkl'))

#Make your cuts here
if PAD_config.makecuts:
  muon_track_cuts(fileID) #Cut tracks
else:
  no_cuts(fileID) #Don't cut any tracks
#Add extra cut functions here?

end = time()
#print(f'File {fileID} elapsed(s): {end-start:.2f}')

#Concatenate all dataframes together
if readop:
  op_df_all = pd.concat(op_dfs)
  op_df_all.to_pickle(f'{DATA_DIR}/op_{sample}_df.pkl')
  print(f'Making {DATA_DIR}/op_{sample}_df.pkl')
if readg4:
  g4_df_all = pd.concat(g4_dfs)
  g4_df_all.to_pickle(f'{DATA_DIR}/g4_{sample}_df.pkl')
  print(f'Making {DATA_DIR}/g4_{sample}_df.pkl')
if readmuon:
  muon_df_all = pd.concat(muon_dfs)
  muon_df_all.to_pickle(f'{DATA_DIR}/muon_{sample}_df.pkl')
  print(f'Making {DATA_DIR}/muon_{sample}_df.pkl')
if readcrt:
  crt_df_all = pd.concat(crt_dfs)
  crt_df_all.to_pickle(f'{DATA_DIR}/crt_{sample}_df.pkl')
  print(f'Making {DATA_DIR}/crt_{sample}_df.pkl')











  



