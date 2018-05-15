import pandas as pd
#import numpy as np

def MkTransforms(rawdf):
    #pass in dataframe with control rows on top following expected format
    #output is the
    #names of id columns, groups for decomps, transforms, knownsigns for models
    #and dataframe with only data that is transformed 
    #get the data
    import pandas as pd
    import numpy as np
    import math as math
    
    #pd.set_option('display.multi_sparse', False)
    #get the data
    #rawdf=pd.read_csv("C:/Users/TeamLorenzen/Documents/App0/static/downloads/ex.csv")
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
    
    #get the data only frame, convert to floats when possible
    datadf=rawdf.iloc[3:rawdf.shape[0],:]
      
    #Adstock transform -- everyone gets a .5 for now!
    retention=0.5
    #forAdstock=rawdf.iloc[3:rawdf.shape[0],needForAdstock]
    #forAdstock=datadf
    #make new vars as name+'_stock'
    #for adstvar in AdstockVs:
    #    forAdstock[adstvar+'_stock']=0
    
    #make dict of sub-DFs by all ID names except the last one, which better be time ID
    #dictAdstockDFs=dict(tuple(forAdstock.groupby(IDnames[0:len(IDnames)-1])))
    dictAdstockDFs=dict(tuple(datadf.groupby(IDnames[0:len(IDnames)-1])))
    
    #apply adstocking to each sub-DF for each variable to be adstocked
    for k in dictAdstockDFs.keys():
        idxmin=min(dictAdstockDFs[k].index.values)
        for idx,row in dictAdstockDFs[k].iterrows():
            for adstvar in AdstockVs:
                adstockedcausal=adstvar+'_stock'
                value=float(row[adstvar])
                #print(count,value)
                if idx==idxmin: #first row is first wweek, needs special care
                    dictAdstockDFs[k].at[idx,adstvar]=value
                    oldvalue=value
                else:
                    dictAdstockDFs[k].at[idx,adstvar]=value+retention*oldvalue
                    oldvalue=value+retention*oldvalue
    #need to recombine them
    datadf=pd.concat(dictAdstockDFs[k] for k in dictAdstockDFs.keys())
    
    try:
        for v in (LogVs):
            datadf[v] = pd.to_numeric(datadf[v])#.apply(lambda x: value(x))
            datadf[v] = datadf[v].apply(lambda x: math.log(x))
    except Exception as e:
        print(e)
        
    #tackling mean center now;  first break into sub dfs again to mean cneter by id vars
    #have to rebuild the dict as the original df has changed
    dictAdstockDFs=dict(tuple(datadf.groupby(IDnames[0:len(IDnames)-1])))
    for k in dictAdstockDFs.keys():
        for vv in MCVs:
            #in case not logged first, need to get to float
            dictAdstockDFs[k][vv] = pd.to_numeric(dictAdstockDFs[k][vv])
            dictAdstockDFs[k][vv]=dictAdstockDFs[k][vv]-dictAdstockDFs[k][vv].mean()
    #need to recombine them
    datadf=pd.concat(dictAdstockDFs[k] for k in dictAdstockDFs.keys())
    #Add dummies for ID variables that are not time (assuming time id is last one!)
    datadf=pd.get_dummies(datadf,columns=IDnames[0:len(IDnames)-1])

    return IDnames, groups, transforms,knownSigns, datadf