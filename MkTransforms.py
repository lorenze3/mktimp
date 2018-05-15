import pandas as pd
#import numpy as np

def MkTransforms(rawdf=):
    #get the data
    import pandas as pd
import numpy as np
import math as math

pd.set_option('display.multi_sparse', False)
#get the data
rawdf=pd.read_csv("C:/Users/TeamLorenzen/Documents/App0/static/downloads/ex.csv")
#make 4 dataframes (or series, I guess)
#1) series of groups for decomps from row 2
#2) series of transforms from row 3
#3) series of sign constraints from row 4

#control information referenced above
groups=rawdf.iloc[0,:]
transforms=rawdf.iloc[1,:]
knownSigns=rawdf.iloc[2,:]

#some useful lists for dataframes below
needForAdstockVs=[i for i, word in enumerate(transforms) if word.startswith('adstock')]
needForAdstockIDs=[i for i,word in enumerate(groups) if word.endswith('id')]
needForAdstock=needForAdstockIDs + needForAdstockVs
needForLogVs = [i for i, word in enumerate(transforms) if word.startswith('log')]
needForMCVs=[i for i, word in enumerate(transforms) if word.endswith('mc')]

#Most Df operations want column names -- so they are made in these lists
IDnames=rawdf.columns.values[needForAdstockIDs].tolist()
AdstockVs=rawdf.columns.values[needForAdstockVs].tolist()
LogVs=rawdf.columns.values[needForLogVs].tolist()
MCVs=rawdf.columns.values[needForMCVs].tolist()
#if time isn't the last id column then this sort will lead to bad adstock
rawdf.sort_values(by=IDnames)
  
#Adstock transform -- everyone gets a .5 for now!
retention=0.5
forAdstock=rawdf.iloc[3:rawdf.shape[0],needForAdstock]
#multi index on id columns minus tid (which is last one in list)for later grouping
#forAdstock.set_index(IDnames[0:len(IDnames)-1],inplace=True)
#make new vars as name+'_stock'
for adstvar in AdstockVs:
    forAdstock[adstvar+'_stock']=0
#make dict of sub-DFs by all ID names except the last one, which better be time ID
dictAdstockDFs=dict(tuple(forAdstock.groupby(IDnames[0:len(IDnames)-1])))

#apply adstocking to each sub-DF for each variable to be adstocked
for k in dictAdstockDFs.keys():
    idxmin=min(dictAdstockDFs[k].index.values)
    for idx,row in dictAdstockDFs[k].iterrows():
        for adstvar in AdstockVs:
            adstockedcausal=adstvar+'_stock'
            value=float(row[adstvar])
            #print(count,value)
            if idx==idxmin: #first row is first wweek, needs special care
                dictAdstockDFs[k].at[idx,adstockedcausal]=value
                oldvalue=value
            else:
                dictAdstockDFs[k].at[idx,adstockedcausal]=value+retention*oldvalue
                oldvalue=value+retention*oldvalue
#need to recombine them
allAdstock= pd.concat(dictAdstockDFs[k] for k in dictAdstockDFs.keys())