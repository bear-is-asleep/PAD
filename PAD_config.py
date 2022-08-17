#!/usr/bin/env python3 
# -*- coding: utf-8 -*- 
#----------------------------------------------------------------------------
# Created By  : Brinden Carlson
# Created Date: August 10, 2022
# version =1.0
# ---------------------------------------------------------------------------
""" Configure parameters for reading PAD tool""" 
# ---------------------------------------------------------------------------

#Imports
import os
cwd = os.getcwd() #Get current directory

mode = 'PAD' #PAD: run PAD, build: prepare data, both: do both
event = 2 #Which event to load, ranges from 0 to number of events -1
DATA_DIR = '/sbnd/data/users/brindenc/analyze_sbnd/PDS/pgun2/data/test6'


#Config parameters for make_pkls.py 
fileID = '' #optional extra deliminator, you can set this to '' for no file id
sample = '' #sample label
readop = True #recob::OpHit
readg4 = True #simb::MCTruth
readcrt = False #sbnd::crt::CRTData
readmuon = True #sbnd::comm::MuonTrack
#readpandoratrack = False #recob::Track (not supported)
#readpandorashower = False #recob::Shower (not supported)
#readgenie = False #simb::MCParticle (not supported)
rootfile = f'hitdumper_tree.root' #Specify root file name
foldername = 'hitdumper' #Folder name inside root file
treename = 'hitdumpertree;1' #Tree name inside folder
#branchname1 = '' #Descend into further branches
#branchname2 = '' #Descend into further branches
uprootname = f'{DATA_DIR}/{rootfile}:{foldername}/{treename}' #Load name for uproot
remakedata = True #Set to true to remake dataset

#Config for make_cuts.py
#apathreshold = 100 #x1 and x2 need to be greater than this to be considered 'near-apa' muon track only
makecuts = False #Run this script?


#Config for sum_PE.py
bw = 0.002 #Time step for summing PE over time bins [us]
leftshift = 12 #How many bins to the left for time slider
rightshift = 20 #How many bins to the right for time slider
readout0 = 0.2 #Center bin based on trigger time - TPC0
readout1 = 0.2 #Center bin based on trigger time - TPC1

#Config for PAD.py
#On startup
#coating: -1 for all, 0 for coated, 1 for uncoated, 2 for vis arapuca, 3 for vuv arapuca, 0.5 for all PMTs, 2.5 for all arapucas
coating = -1
tpc = 0 #TPC
df_label = 'summed_PE' #Start colorscale, options given by scalardf.keys() or vectordf.keys()

#PAD
textcolor = 'white'
labelcolor = 'black'
facecolor = 'black'
figcolor = 'gray'
cmap = 'hot'
markboxes = False
#Lines
plotg4 = True
plotmuon = True
showlegend = True
#Slider/boxes
fillcolor = 'teal'
boxfacecolor = 'lightgoldenrodyellow'
handlesize = 50

#Other vars
bc_pad_dir = '/sbnd/app/users/brindenc/analyze_sbnd/PMT/timing/PAD'
tlow = -999 #Min acceptance readout window for g4 track [ms]
thigh = 999 #Max acceptance readout window for g4 track [ms]
g4keys = ['no_primaries',
 'geant_list_size',
 'pdg',
 'status',
 'Eng',
 'EndE',
 'Mass',
 'Px',
 'Py',
 'Pz',
 'P',
 'StartPointx',
 'StartPointy',
 'StartPointz',
 'StartT',
 'EndT',
 'EndPointx',
 'EndPointy',
 'EndPointz',
 'theta_xz',
 'theta_yz',
 'pathlen',
 'NumberDaughters',
 'TrackId',
 'Mother']








