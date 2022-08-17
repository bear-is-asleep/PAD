#!/sbnd/data/users/brindenc/.local/bin/python3.9
import sys
sys.path.append('/sbnd/data/users/brindenc/.local/lib/python3.9/site-packages')
sys.path.append('/sbnd/app/users/brindenc/mypython') #My utils path
sys.path.append('.')
import PAD_config
import numpy as np
from matplotlib.widgets import Slider, Button, RadioButtons
import matplotlib.pyplot as plt
from bc_utils.pmtutils import pic as pmtpic
from bc_utils.pmtutils import plotters as pmtplotters
from bc_utils.utils import pic,plotters
import pandas as pd
import matplotlib.image as mpimg
import matplotlib.lines as mlines

#File info
DATA_DIR = PAD_config.DATA_DIR #Where's your data going?
sample = PAD_config.sample #Sample name
tpc = PAD_config.tpc #Which tpc to start in? Probably 0
ind = PAD_config.event #Which event to load, ranges from 0 to number of events -1
df_label=PAD_config.df_label #Colorscale
coating=PAD_config.coating #Load start coating

#Read events
readg4 = PAD_config.readg4
readop = PAD_config.readop
readcrt = PAD_config.readcrt
readmuon = PAD_config.readmuon

#Define extra functions
def findvmax(df,coating,df_label):
  #Decide max colorscale
  #print(coating,df_label,df.head())
  if df_label == 'summed_PE': #Do this to properly set max val to cumsum PE
    df_label = 'tot_PE'
  if coating == -1:
    vmax =  df.loc[:,df_label].values.max()
  elif coating == 1 or coating == 0 or coating == 2 or coating == 3:
    vmax = df[df.loc[:,'ophit_opdet_type'] == coating].loc[:,df_label].values.max()
  elif coating == 2.5: #All x-arapucas
    max1 = df[df.loc[:,'ophit_opdet_type'] == 2].loc[:,df_label].values.max()
    max2 = df[df.loc[:,'ophit_opdet_type'] == 3].loc[:,df_label].values.max()
    vmax = max([max1,max2]) #Max between two values
  elif coating == 0.5: #All pmts
    max1 = df[df.loc[:,'ophit_opdet_type'] == 0].loc[:,df_label].values.max()
    max2 = df[df.loc[:,'ophit_opdet_type'] == 1].loc[:,df_label].values.max()
    vmax = max([max1,max2]) #Max between two values
  return vmax

def load_dfs(sample,tpc,loadg4=True,loadmuon=True):
  #Legend labels for plotting
  labels = []

  #Make dataframes
  scalarPE_df = pd.read_pickle(f'{DATA_DIR}/scalarPE{tpc}_{sample}_df.pkl')
  vectorPE_df = pd.read_pickle(f'{DATA_DIR}/vectorPE{tpc}_{sample}_df.pkl')
  indeces = scalarPE_df.index.drop_duplicates()

  index = indeces[ind]

  scalarPE_df = scalarPE_df.sort_index()
  vectorPE_df = vectorPE_df.sort_index()

  #Keep single event
  scalardf = scalarPE_df.loc[index]
  vectordf = vectorPE_df.loc[index]

  dfs = [scalardf,vectordf]

  #Load dataframes for plotting
  if loadmuon:
    muon_df = pd.read_pickle(f'{DATA_DIR}/muon_{sample}_df.pkl')
    muon_df = muon_df.sort_index()
    #Clean data - print trajectory through tpc
    muon_plot_df = muon_df.drop(['nmuontrks','muontrk_t0'],axis=1)
    muon_plot_df = pmtpic.get_muon_tracks(muon_plot_df)
    muon_plot_df = muon_plot_df.set_index(['run','subrun','event'])
    #muon_plot_df = muon_plot_df.loc[index]
    #Print statements
    pic.print_stars()
    print(f'Making plot for Run {index[0]} Subrun {index[1]} Event {index[2]} TPC{tpc}')
    if tpc == 0:
      x1 = muon_plot_df.loc[index,'muontrk_x1_0']
      x2 = muon_plot_df.loc[index,'muontrk_x2_0']
      y1 = muon_plot_df.loc[index,'muontrk_y1_0']
      y2 = muon_plot_df.loc[index,'muontrk_y2_0']
      z1 = muon_plot_df.loc[index,'muontrk_z1_0']
      z2 = muon_plot_df.loc[index,'muontrk_z2_0']
    if tpc == 1:
      x1 = muon_plot_df.loc[index,'muontrk_x1_1']
      x2 = muon_plot_df.loc[index,'muontrk_x2_1']
      y1 = muon_plot_df.loc[index,'muontrk_y1_1']
      y2 = muon_plot_df.loc[index,'muontrk_y2_1']
      z1 = muon_plot_df.loc[index,'muontrk_z1_1']
      z2 = muon_plot_df.loc[index,'muontrk_z2_1']

    if isinstance(x1,np.int64):
      print(f'Muon moves from [{x1:.0f},{y1:.0f},{z1:.0f}] to [{x2:.0f},{y2:.0f},{z2:.0f}]')
    else:
      for i in range(len(x1)):
        print(f'Muon {i} moves from [{x1.iloc[i]:.0f},{y1.iloc[i]:.0f},{z1.iloc[i]:.0f}] to [{x2.iloc[i]:.0f},{y2.iloc[i]:.0f},{z2.iloc[i]:.0f}]')

    pic.print_stars()
    dfs.append(muon_df)
    labels.append('Muon')
  if loadg4:
    g4_df = pd.read_pickle(f'{DATA_DIR}/g4_{sample}_df.pkl')
    g4_df = g4_df.sort_index()
    dfs.append(g4_df)
    labels.append('G4')

  return dfs,index,labels

#Define style
#plt.style.use('science')

#Pass event to display
#argList = sys.argv[1:]

#Handle people who don't know how to run this
#if len(argList)<2:
#  raise Exception(f'You should specify an event for the first input.\nSecondly you should specify the tpc (0 or 1)\nThe last value should specify sample type (ew or fb)')
#else: 
#  tpc = int(argList[1])
#  ind = int(argList[0])
#  sample = argList[2]


#Make dataframes
dfs,index,labels = load_dfs(sample,tpc,loadg4=readg4,loadmuon=readmuon)
scalardf = dfs[0]
vectordf = dfs[1]
if readg4 and readmuon:
  muon_df = dfs[2]
  g4_df = dfs[3]
elif readg4 and not readmuon:
  g4_df =dfs[2]
elif not readg4 and readmuon:
  muon_df =dfs[2]


trights = vectordf.loc[index,'tright'].drop_duplicates().values #Use this for slider value
tleft = scalardf.loc[:,'tleft'].drop_duplicates().values[0] #First time PE is seen
#Constants/initialize
cdict = {'PE':'summed_PE',
          'Channels':'ophit_opch',
          'Coatings':'ophit_opdet_type'} #Dictionary for coloring and labeling points
tdict = {'All':-1,
          'X-ARAPUCA':2.5,
          'PMT':0.5,
          'Coated PMT':0,
          'Uncoated PMT':1,
          'VIS X-ARAPUCA':2,
          'VUV X-ARAPUCA':3} #Dictionary for coating type
tpcdict = {'TPC0 - West APA':0,
           'TPC1 - East APA':1} #Dictionary for TPC

#PAD
textcolor = PAD_config.textcolor
labelcolor = PAD_config.labelcolor
facecolor = PAD_config.facecolor
figcolor = PAD_config.figcolor
cmap = PAD_config.cmap
markboxes = PAD_config.markboxes
#Lines
plotg4 = readg4
plotmuon = readmuon
show_legend = PAD_config.showlegend
thigh=PAD_config.thigh
tlow=PAD_config.tlow
#Slider/boxes
fillcolor = PAD_config.fillcolor
boxfacecolor = PAD_config.boxfacecolor
handlesize = PAD_config.handlesize



#Initial params
tright = round(trights[3],3) #Initialize right bound
title = f'PE for t$\in$[{tleft:.3f},{tright:.3f}] $\mu$s '
init_cs = vectordf[round(vectordf.loc[:,'tright'],3) == tright]#Initial colors, specify key later?
df = pd.concat([init_cs,scalardf],axis=1)
df = df.loc[:,~df.columns.duplicated()] #Remove duplicate columns
vmax = findvmax(df,coating,df_label)

#Make initial plot
fig,ax,sc,cax = pmtplotters.interactive_TPC(tpc,df_label,title,df,coating=coating,cmap=cmap,
  return_plot=True,normalize=False,facecolor=facecolor,ax=None,fig=None,vmax=vmax,text_label=df_label,
  textcolor=textcolor,markboxes=markboxes,figcolor=figcolor)
lines = [] #Save plot lines to make legend
#Make sure these if statements are in the same order as they are in load_df
if plotmuon:
  temp_muon = muon_df[muon_df.loc[:,'muontrk_tpc'] == tpc]
  if index in list(temp_muon.index.drop_duplicates()):
    line = pmtplotters.plot_tracks(temp_muon.loc[index],'muontrk_z1','muontrk_y1','muontrk_z2','muontrk_y2',ax,
      alpha=0.5,linewidth=10,linestyle='-')
    lines.append(line)
  else:
    line = mlines.Line2D([],[],alpha=0.5,linewidth=10,linestyle='-')
    lines.append(line)
if plotg4:
  line = pmtplotters.plot_tracks(g4_df.loc[index],'StartPointz','StartPointy','EndPointz','EndPointy',ax,
  alpha=0.75,linewidth=5,linestyle='-.')
  lines.append(line)
ax.legend(handles=lines,labels=labels,bbox_to_anchor=(1,1.1))





#Vertical slider
axtright = fig.add_axes([0.05,0.9,0.9,0.02],facecolor=boxfacecolor)
tright_slider = Slider(
ax=axtright,
label=r'$t_{max}$',
valmin=trights[0],
valmax=trights[-1],
valstep=trights, #Set valstep to constant binwidth
valinit=tright,
orientation='horizontal',
initcolor=None,
color=fillcolor
)

def update(val):
  global ax
  global fig
  global sc
  global cax
  global df
  global title
  global df_label
  global coating
  global tright
  global tpc
  global vectordf
  global scalardf
  del ax.texts[:] #Remove all text from figure
  tright = round(val,3)
  title = f'PE for t$\in$[{tleft:.3f},{tright:.3f}] $\mu$s '
  cs = vectordf[round(vectordf.loc[:,'tright'],5) == tright]#Initial colors, specify key later?
  df = pd.concat([cs,scalardf],axis=1)
  df = df.loc[:,~df.columns.duplicated()] #Remove duplicate columns
  sc.remove()
  cax.remove()
  vmax = findvmax(df,coating,df_label)
  fignew,axnew,scnew,caxnew = pmtplotters.interactive_TPC(tpc,df_label,title,df,coating=coating,cmap=cmap,
    return_plot=True,normalize=False,facecolor=facecolor,ax=ax,fig=fig,vmax=vmax,text_label=df_label,
    textcolor=textcolor,markboxes=markboxes,figcolor=figcolor)
  fig = fignew
  ax = axnew
  sc = scnew
  cax = caxnew
  
  
#Register slider value
tright_slider.on_changed(update)

#Select colors/text
radiocolor=boxfacecolor
axradio1 = fig.add_axes([0.825,0.1,0.1,0.15],facecolor=radiocolor)
radio1 = RadioButtons(axradio1,('PE','Channels','Coatings'))
def colorbuttons(label): #Color button update function
  global ax
  global fig
  global sc
  global cax
  global df
  global title
  global df_label
  global coating
  global tright
  global tpc
  global vectordf
  global scalardf
  df_label = cdict[label] #Pass this key into interactive tpc

  del ax.texts[:] #Remove all text from figure
  sc.remove() #Remove scatter poitns
  cax.remove() #Remove coloscale
  vmax = findvmax(df,coating,df_label)
  fignew,axnew,scnew,caxnew = pmtplotters.interactive_TPC(tpc,df_label,title,df,coating=coating,cmap=cmap,
    return_plot=True,normalize=False,facecolor=facecolor,ax=ax,fig=fig,vmax=vmax,text_label=df_label,
    textcolor=textcolor,markboxes=markboxes,figcolor=figcolor)
  fig = fignew
  ax = axnew
  sc = scnew
  cax = caxnew
  plt.draw()
radio1.on_clicked(colorbuttons)

axradio2 = fig.add_axes([0.825,0.3,0.1,0.15],facecolor=radiocolor)
radio2 = RadioButtons(axradio2,('All','X-ARAPUCA','PMT','Coated PMT','Uncoated PMT','VIS X-ARAPUCA','VUV X-ARAPUCA'))
def coatingbuttons(label): #Color button update function
  global ax
  global fig
  global sc
  global cax
  global df
  global title
  global df_label
  global coating
  global tright
  global tpc
  global vectordf
  global scalardf
  coating = tdict[label] #Pass this key into interactive tpc
  #Decide max colorscale
  vmax = findvmax(df,coating,df_label)
    

  del ax.texts[:] #Remove all text from figure
  sc.remove() #Remove scatter poitns
  cax.remove() #Remove coloscale
  fignew,axnew,scnew,caxnew = pmtplotters.interactive_TPC(tpc,df_label,title,df,coating=coating,cmap=cmap,
    return_plot=True,normalize=False,facecolor=facecolor,ax=ax,fig=fig,vmax=vmax,text_label=df_label,
    textcolor=textcolor,markboxes=markboxes,figcolor=figcolor)
  fig = fignew
  ax = axnew
  sc = scnew
  cax = caxnew
  plt.draw()
radio2.on_clicked(coatingbuttons)

axradio3 = fig.add_axes([0.825,0.5,0.1,0.15],facecolor=radiocolor)
radio3 = RadioButtons(axradio3,('TPC0 - West APA','TPC1 - East APA'))
def tpcbuttons(label): #Color button update function
  global ax
  global fig
  global sc
  global cax
  global df
  global title
  global df_label
  global coating
  global tright
  global tpc
  global vectordf
  global scalardf
  tpc = tpcdict[label] #Pass this key into interactive tpc
  dfs,index,_ = load_dfs(sample,tpc,loadmuon=readmuon,loadg4=False)
  scalardf = dfs[0]
  vectordf = dfs[1]
  if readmuon:
    muon_df = dfs[2]

  cs = vectordf[round(vectordf.loc[:,'tright'],3) == tright]#Initial colors, specify key later?
  df = pd.concat([cs,scalardf],axis=1)
  df = df.loc[:,~df.columns.duplicated()] #Remove duplicate columns

  title = f'PE for t$\in$[{tleft:.3f},{tright:.3f}] $\mu$s '
  #Decide max colorscale
  vmax = findvmax(df,coating,df_label)
  del ax.texts[:] #Remove all text from figure
  sc.remove() #Remove scatter poitns
  cax.remove() #Remove coloscale
  #ax.get_legend().remove() #Remove legend
  del ax.lines[:] #Remove tracks
  if markboxes:
    pmtplotters.make_lines(ax=ax) #Add boundary lines again
  fignew,axnew,scnew,caxnew = pmtplotters.interactive_TPC(tpc,df_label,title,df,coating=coating,cmap=cmap,
    return_plot=True,normalize=False,facecolor=facecolor,ax=ax,fig=fig,vmax=vmax,text_label=df_label,
    textcolor=textcolor,markboxes=markboxes,figcolor=figcolor)
  lines = [] #Save plot lines to make legend
  ax = axnew
  #Make sure these if statements are in the same order as they are in load_df
  if plotmuon:
    temp_muon = muon_df[muon_df.loc[:,'muontrk_tpc'] == tpc]
    if index in list(temp_muon.index.drop_duplicates()):
      line = pmtplotters.plot_tracks(temp_muon.loc[index],'muontrk_z1','muontrk_y1','muontrk_z2','muontrk_y2',ax,
        alpha=0.5,linewidth=10,linestyle='-')
      lines.append(line)
    else:
      line = mlines.Line2D([],[],alpha=0.5,linewidth=10,linestyle='-')
      lines.append(line)
  if plotg4:
    line = pmtplotters.plot_tracks(g4_df.loc[index],'StartPointz','StartPointy','EndPointz','EndPointy',ax,
    alpha=0.75,linewidth=5,linestyle='-.')
    lines.append(line)
  ax.legend(handles=lines,labels=labels,bbox_to_anchor=(1,1.1))
  
  
  fig = fignew
  sc = scnew
  cax = caxnew
  plt.draw()
radio3.on_clicked(tpcbuttons)

#Add sbndlogo
axsbnd = fig.add_axes([0.825,0.7,0.1,0.15])
sbnd = mpimg.imread(f'{PAD_config.bc_pad_dir}/Images/SBND-color.jpg')
axsbnd.imshow(sbnd)
axsbnd.axis('off');

plt.show()
