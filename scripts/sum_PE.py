#!/sbnd/data/users/brindenc/.local/bin/python3.9
import sys
sys.path.append('/sbnd/data/users/brindenc/.local/lib/python3.9/site-packages')
sys.path.append('/sbnd/app/users/brindenc/mypython') #My utils path
sys.path.append('.')
import numpy as np
import PAD_config
from bc_utils.pmtutils import pic as pmtpic
from bc_utils.pmtutils import plotters as pmtplotters
from bc_utils.utils import pic,plotters
from bc_utils.crtutils import pic as crtpic
import pandas as pd
from time import time

pic.print_stars()
print('Running sum_PE.py')

#Make cumulative sum for PE in each bin

#Select which sample to look at
#argList = sys.argv[1:]
#sample = argList[0]
#sample = 'gun0'

#crt_df = pd.read_pickle(f'{DATA_DIR}/crt_{sample}_df.pkl')

#if len(argList) > 1:
#  event_list = argList[1] #Get list of events from second argument
#  indeces = indeces[event_list] #Truncate list to samples you want!

#File info
DATA_DIR = PAD_config.DATA_DIR #Where's your data going?
sample = PAD_config.sample #Sample name

#Read events
readg4 = PAD_config.readg4
readop = PAD_config.readop
readcrt = PAD_config.readcrt
readmuon = PAD_config.readmuon

#Load dataframes - I know we have the option of not loading these, but for this part it'll be non negotiable if you want to sum PE for readop
if readop:
  op_df = pd.read_pickle(f'{DATA_DIR}/op_{sample}_df.pkl')
if readmuon:
  muon_df = pd.read_pickle(f'{DATA_DIR}/muon_{sample}_df.pkl')
indeces = op_df.index.drop_duplicates().values #Set indeces to 
#pmts = pd.read_pickle('data/PMT_info.pkl')
pmts = pd.read_pickle('/sbnd/data/users/brindenc/analyze_sbnd/PDS/PMT_ARAPUCA_info.pkl')



#Parameters
bw = PAD_config.bw #binwidth
leftshift = PAD_config.leftshift 
rightshift = PAD_config.rightshift
readout0 = PAD_config.readout0 #us
readout1 = PAD_config.readout1 #us
trights_size = leftshift+rightshift+1 #Length of trights array
  
#PMT info
channels = pmts.loc[:,'ophit_opdet'].drop_duplicates().values #Channels
channels0 = [ch for ch in channels if ch%2 == 0] #Keep only PDS comps in tpc0
channels1 = [ch for ch in channels if ch%2 == 1] #Keep only PDS comps in tpc1

columns = ['run','subrun','event','ophit_opch','ophit_opdet_type',
          'op_tpc','tleft','tot_PE','ophit_opdet_x',
          'ophit_opdet_y','ophit_opdet_z']
vector_columns = ['summed_PE','tright','run','subrun','event','ophit_opch','ophit_opdet_type']

if readmuon:
  #TPC0   
  muon_df0 = muon_df[muon_df.loc[:,'muontrk_tpc'] == 0].sort_index()
  muon_indeces0 = muon_df0.index.drop_duplicates()
  #TPC1   
  muon_df1 = muon_df[muon_df.loc[:,'muontrk_tpc'] == 1].sort_index()
  muon_indeces1 = muon_df1.index.drop_duplicates()
#TPC0   
scalar_arr0 = np.full((len(indeces),len(channels0),len(columns)),-9999.) #Array with single value for each element
vector_arr0 = np.full((len(indeces),len(channels0),trights_size,len(vector_columns)),-9999.) #Array with vector for each element
#TPC0   
scalar_arr1 = np.full((len(indeces),len(channels1),len(columns)),-9999.) #Array with single value for each element
vector_arr1 = np.full((len(indeces),len(channels1),trights_size,len(vector_columns)),-9999.) #Array with vector for each element

#CRTs
if readcrt:
  #CRT info
  #modules = crt_df.loc[:,'crt_module'].drop_duplicates().values #Module IDs  
  crt_columns = ['run','subrun','event','crt_module','crt_pos_x','crt_pos_y',
    'crt_pos_z','tot_ADC','tleft']
  crt_vector_columns = ['summed_ADC','tright','run','subrun','event','crt_module']
  #crt_arr = np.full((len(indeces),len(modules),len(crt_columns)),-9999)
  #crt_vector = np.full((len(indeces),len(modules),trights_size,len(crt_vector_columns)),-9999)

pic.print_stars() #Start print statement
for i,index in enumerate(indeces): #Iterate over events
  event_start = time() #Time the event
  #Check one TPC at a time

  #TPC 0
  peakT0 = readout0 #Can update this later with t0 finder
  tright0 = np.arange(peakT0-leftshift*bw,peakT0+rightshift*bw,bw)
  #Check for mismatch in size
  if len(tright0) == trights_size+1:
    tright0 = np.delete(tright0,-1,axis=1) #remove last element for all bins (not a big deal to lose 2 ns)
  if len(tright0) == trights_size-1:
    tright0 = np.insert(tright0,0,peakT0-(leftshift+1)*bw) #add a another bin to the left, this also shouldn't do anything bad
  for j,ch in enumerate(channels0):  #Iterate over channels
    channel_start = time()

    #TPC0 for each channel
    bincenters0,yvals0,_ = pmtpic.get_xy_bins(op_df,'ophit_peakT','ophit_pe',index,bw,pmt=ch,tpc=0,xmin=tright0[0],xmax=tright0[-1])
    if len(yvals0) == trights_size + 1:
      yvals0 = np.delete(yvals0,-1) #remove last element for all bins (not a big deal to lose 2 ns)
    #Vector arr - TPC0
    vector_arr0[i,j,:,0] = np.cumsum(yvals0) #PE in region for channel, sum over previous bins
    vector_arr0[i,j,:,1] = tright0 #right bound values
    vector_arr0[i,j,:,2] = np.full(len(yvals0),index[0]) #run
    vector_arr0[i,j,:,3] = np.full(len(yvals0),index[1]) #subrun
    vector_arr0[i,j,:,4] = np.full(len(yvals0),index[2]) #event 
    vector_arr0[i,j,:,5] = np.full(len(yvals0),ch) #ch
    vector_arr0[i,j,:,6] = np.full(len(yvals0),pmts[pmts.loc[:,'ophit_opdet'] == ch].loc[:,'ophit_opdet_type'].drop_duplicates().values[0]) #det type
    #Scalar arr
    scalar_arr0[i,j,0] = index[0] #run
    scalar_arr0[i,j,1] = index[1] #subrun
    scalar_arr0[i,j,2] = index[2] #event
    scalar_arr0[i,j,3] = ch #channel/pmt
    #Get coating type
    scalar_arr0[i,j,4] = pmts[pmts.loc[:,'ophit_opdet'] == ch].loc[:,'ophit_opdet_type'].drop_duplicates().values[0]
    #Get PMT tpc
    scalar_arr0[i,j,5] = pmts[pmts.loc[:,'ophit_opdet'] == ch].loc[:,'opdet_tpc'].drop_duplicates().values[0]
    scalar_arr0[i,j,6] = tright0[0] #left bound
    scalar_arr0[i,j,7] = yvals0.sum() #Total sum of PE
    scalar_arr0[i,j,8] = pmts[pmts.loc[:,'ophit_opdet'] == ch].loc[:,'ophit_opdet_x'].drop_duplicates().values[0]
    scalar_arr0[i,j,9] = pmts[pmts.loc[:,'ophit_opdet'] == ch].loc[:,'ophit_opdet_y'].drop_duplicates().values[0]
    scalar_arr0[i,j,10] = pmts[pmts.loc[:,'ophit_opdet'] == ch].loc[:,'ophit_opdet_z'].drop_duplicates().values[0]
  #TPC 1
  peakT1 = readout1 #Can update this later with t1 finder
  tright1 = np.arange(peakT1-leftshift*bw,peakT1+rightshift*bw,bw)
  #Check for mismatch in size
  if len(tright1) == trights_size+1:
    #print('I did  it')
    tright1 = np.delete(tright1,-1,axis=1) #remove last element for all bins (not a big deal to lose 2 ns)
  if len(tright1) == trights_size-1:
    #print('WTF')
    tright1 = np.insert(tright1,0,peakT1-(leftshift+1)*bw) #add a another bin to the left, this also shouldn't do anything bad
  #print(tright1)
  for j,ch in enumerate(channels1):  #Iterate over channels
    channel_start = time()

    #TPC1 for each channel
    bincenters1,yvals1,_ = pmtpic.get_xy_bins(op_df,'ophit_peakT','ophit_pe',index,bw,pmt=ch,tpc=1,xmin=tright1[0],xmax=tright1[-1])
    if len(yvals1) == trights_size + 1:
      yvals1 = np.delete(yvals1,-1) #remove last element for all bins (not a big deal to lose 2 ns)
    #print(ch,bincenters1, yvals1,yvals1.shape,bincenters1.shape)
    #print(tright1)
    #Vector arr - TPC1
    vector_arr1[i,j,:,0] = np.cumsum(yvals1) #PE in region for channel, sum over previous bins
    vector_arr1[i,j,:,1] = tright1 #right bound values
    vector_arr1[i,j,:,2] = np.full(len(yvals1),index[0]) #run
    vector_arr1[i,j,:,3] = np.full(len(yvals1),index[1]) #subrun
    vector_arr1[i,j,:,4] = np.full(len(yvals1),index[2]) #event 
    vector_arr1[i,j,:,5] = np.full(len(yvals1),ch) #ch
    vector_arr1[i,j,:,6] = np.full(len(yvals1),pmts[pmts.loc[:,'ophit_opdet'] == ch].loc[:,'ophit_opdet_type'].drop_duplicates().values[0]) #det type
    #Scalar arr
    scalar_arr1[i,j,0] = index[0] #run
    scalar_arr1[i,j,1] = index[1] #subrun
    scalar_arr1[i,j,2] = index[2] #event
    scalar_arr1[i,j,3] = ch #channel/pmt
    #Get coating type
    scalar_arr1[i,j,4] = pmts[pmts.loc[:,'ophit_opdet'] == ch].loc[:,'ophit_opdet_type'].drop_duplicates().values[0]
    #Get PMT tpc
    scalar_arr1[i,j,5] = pmts[pmts.loc[:,'ophit_opdet'] == ch].loc[:,'opdet_tpc'].drop_duplicates().values[0]
    scalar_arr1[i,j,6] = tright1[0] #left bound
    scalar_arr1[i,j,7] = yvals1.sum() #Total sum of PE
    scalar_arr1[i,j,8] = pmts[pmts.loc[:,'ophit_opdet'] == ch].loc[:,'ophit_opdet_x'].drop_duplicates().values[0]
    scalar_arr1[i,j,9] = pmts[pmts.loc[:,'ophit_opdet'] == ch].loc[:,'ophit_opdet_y'].drop_duplicates().values[0]
    scalar_arr1[i,j,10] = pmts[pmts.loc[:,'ophit_opdet'] == ch].loc[:,'ophit_opdet_z'].drop_duplicates().values[0]
    channel_end = time()
    # for j,module in enumerate(modules):
    #   bincenters,yvals,_ = crtpic.get_xy_bins(crt_df,'crt_time','crt_adc',index,bw,module=module,
    #         xmin=tright0[0],xmax=tright0[-1]) #Get timing and adc of all crts

    #   crt_vector[i][j][:,0] = yvals #adc for module
    #   crt_vector[i][j][:,1] = bincenters #time bins for module
    #   crt_vector[i][j][:,2] = np.full(len(yvals),index[0]) #run
    #   crt_vector[i][j][:,3] = np.full(len(yvals),index[1]) #subrun
    #   crt_vector[i][j][:,4] = np.full(len(yvals),index[2]) #event
    #   crt_vector[i][j][:,5] = np.full(len(yvals),module) #module

    #   crt_arr[i][j][0] = index[0] #run
    #   crt_arr[i][j][1] = index[1] #subrun
    #   crt_arr[i][j][2] = index[2] #event
    #   crt_arr[i][j][3] = index[3] #module
    #   crt_arr[i][j][4] = crt_df[crt_df.loc[:,'crt_module'] == module].loc[:,'crt_pos_x'].drop_duplicates().values[0] #x position for this channel
    #   crt_arr[i][j][5] = crt_df[crt_df.loc[:,'crt_module'] == module].loc[:,'crt_pos_y'].drop_duplicates().values[0] #x position for this channel
    #   crt_arr[i][j][6] = crt_df[crt_df.loc[:,'crt_module'] == module].loc[:,'crt_pos_z'].drop_duplicates().values[0] #x position for this channel
    #   crt_arr[i][j][7] = yvals.sum() #total adc
    #   crt_arr[i][j][8] = peakT0 #left bound
      

    #print(f'Channel {ch} time: {channel_end-channel_start} s')
  event_end = time()
  print(f'Run {index[0]} Subrun {index[1]} Event {index[2]} time: {event_end-event_start:.2f} s')


#Convert to dataframe - TPC0
scalar_arr0 = scalar_arr0.reshape(len(indeces)*len(channels0),len(columns))
vector_arr0 = vector_arr0.reshape(len(indeces)*len(channels0)*trights_size,len(vector_columns))
scalar_df0 = pd.DataFrame(scalar_arr0,columns=columns)
vector_df0 = pd.DataFrame(vector_arr0,columns=vector_columns)



#Convert to dataframe - TPC1
scalar_arr1 = scalar_arr1.reshape(len(indeces)*len(channels1),len(columns))
vector_arr1 = vector_arr1.reshape(len(indeces)*len(channels1)*len(tright1),len(vector_columns))#scalar_df1 = pd.DataFrame(scalar_arr1,columns=columns)
scalar_df1 = pd.DataFrame(scalar_arr1,columns=columns)
vector_df1 = pd.DataFrame(vector_arr1,columns=vector_columns)

#Convert to dataframe - CRT
#crt_arr = crt_arr.reshape(len(indeces)*len(modules),len(crt_columns))
#crt_vector = crt_vector.reshape(len(indeces)*len(modules)*trights_size,len(crt_vector_columns))
#crt_arr_df = pd.DataFrame(crt_arr,columns=crt_columns)
#crt_vector_df = pd.DataFrame(crt_vector,columns=crt_vector_columns)

#TPC0
scalar_df0 = scalar_df0.set_index(['run','subrun','event'])
vector_df0 = vector_df0.set_index(['run','subrun','event'])

#Drop null values
#scalar_df0 = scalar_df0.drop(index=(-9999,-9999,-9999))
#vector_df0 = vector_df0.drop(index=(-9999,-9999,-9999))
#Save pkl files
scalar_df0.to_pickle(f'{DATA_DIR}/scalarPE0_{sample}_df.pkl')
vector_df0.to_pickle(f'{DATA_DIR}/vectorPE0_{sample}_df.pkl')

#TPC1
scalar_df1 = scalar_df1.set_index(['run','subrun','event'])
vector_df1 = vector_df1.set_index(['run','subrun','event'])
#Save pkl files
scalar_df1.to_pickle(f'{DATA_DIR}/scalarPE1_{sample}_df.pkl')
vector_df1.to_pickle(f'{DATA_DIR}/vectorPE1_{sample}_df.pkl')

#CRT
#crt_arr_df = crt_arr_df.set_index(['run','subrun','event'])
#crt_vector_df = crt_vector_df.set_index(['run','subrun','event'])
#Save pkl files
#crt_arr_df.to_pickle(f'{DATA_DIR}/crtarr_{sample}_df.pkl')
#crt_vector_df.to_pickle(f'{DATA_DIR}/crtvector_{sample}_df.pkl')





