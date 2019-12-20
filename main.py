import ROOT
import numpy as np
import glob
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json
import collections

sns.set_context('poster')
sns.set(font_scale=1.4)

DATEDB = "./DB/RunDate.json"
GAINDB = "./DB/TransparencyGains.json"

DATAPATH = "./data/Transparency/"

if __name__ == "__main__":
    LEDS = [6]
    TUBES = [356,357,360,364,365,367,368,370]
    intensity_bases = {}
    relative_intensities = [1.0]
    relative_intensity_stdevs = [0.0]
    alldata = {"run":[], "LED":[], "date":[],"channel":[],
            "relative_mean":[], "charge_mean":[],"QPerPE":[],
            "QPerPEUnc":[]}
    
    data = None
    with open(DATEDB,"r") as f:
        data = json.load(f, object_pairs_hook=collections.OrderedDict)
    gaindata = None
    with open(GAINDB,"r") as f:
        gaindata = json.load(f)
    gd = pd.DataFrame(gaindata["Gauss2"])

    for j,date in enumerate(data):
        print(date)
        r = int(data[date])
        for k,l in enumerate(LEDS):
            myfile = ROOT.TFile.Open("%sLEDRun%iS0LED%i_AllPMTs_PMTStability_Run0.root"%(DATAPATH,r,l))
            these_means = []
            for t in TUBES:
                myhist = myfile.Get("hist_charge_%i"%(t))
                themean = myhist.GetMean()
                if j==0:
                    alldata["run"].append(r)
                    alldata["LED"].append(l)
                    alldata["date"].append(date)
                    alldata["channel"].append(t)
                    alldata["charge_mean"].append(themean)
                    alldata["QPerPE"].append(gd.loc[gd["Channel"] == t, 'c1Mu'].mean())
                    alldata["QPerPEUnc"].append(gd.loc[gd["Channel"] == t, 'c1Mu'].std())
                    alldata["relative_mean"].append(1.0)
                    intensity_bases[t] = themean
                else:
                    alldata["run"].append(r)
                    alldata["LED"].append(l)
                    alldata["date"].append(date)
                    alldata["channel"].append(t)
                    alldata["QPerPE"].append(gd.loc[gd["Channel"] == t, 'c1Mu'].mean())
                    alldata["QPerPEUnc"].append(gd.loc[gd["Channel"] == t, 'c1Mu'].std())
                    alldata["charge_mean"].append(themean)
                    alldata["relative_mean"].append(themean/intensity_bases[t])
    print("RELATIVE MEANS:")
    print(alldata["relative_mean"])
    ndpd = pd.DataFrame(alldata)
    fig = plt.figure()
    ax = sns.barplot(x='date',y='relative_mean',estimator=np.mean,
            data=ndpd)
    ax.set_xlabel("Date") 
    ax.set_ylabel("Charge mean average, relative to first day") 
    plt.xticks(rotation='30',fontsize=10)
    plt.title(("Average of ETEL charge means (all PMTs normalized to first day)\n" +
        "LED 6 only (PIN 3500)"))
    plt.show()

    fig = plt.figure()
    ax = sns.pointplot(x='date',y='charge_mean',hue='channel',
            data=ndpd)
    ax.set_xlabel("Date") 
    ax.set_ylabel("PMT charge mean (nC)") 
    plt.xticks(rotation='30',fontsize=12)
    plt.title(("Mean of charge distribution from ETEL tubes flashed with \n" +
        "LED 6 only (PIN 3500)"))
    plt.show()

    fig = plt.figure()
    ax = sns.pointplot(x='date',y='relative_mean',hue='channel',
            data=ndpd)
    ax.set_xlabel("Date") 
    ax.set_ylabel("PMT charge mean, normalized to first day") 
    plt.xticks(rotation='30')
    plt.title(("ETEL charge means (normalized to first day) \n" +
        "LED 6 only (PIN 3500)"))
    plt.show()

    fig,ax = plt.subplots()
    ndpd["PE"] = ndpd["charge_mean"]/ndpd["QPerPE"]
    ndpd["PEUnc"] = (ndpd["charge_mean"]/(ndpd["QPerPE"]**2))*ndpd["QPerPEUnc"]
    
    ndpd["PE"] = ndpd["charge_mean"]/ndpd["QPerPE"]
    ndpd["PEUnc"] = (ndpd["charge_mean"]/(ndpd["QPerPE"]**2))*ndpd["QPerPEUnc"]
    dates = []
    date_sums = []
    date_stdevs = []
    for j,date in enumerate(data):
        dates.append(date)
        print("RESULT IS: ")
        print(ndpd.loc[ndpd["date"] == date, 'PE'])
        date_sums.append(float((ndpd.loc[(ndpd["date"] == date), 'PE'].sum())))
        QToPE_err = np.linalg.norm((ndpd.loc[(ndpd["date"] == date), 'PEUnc']))
        IErr = np.sqrt((date_sums[j]*0.005)**2)
        date_stdevs.append(np.sqrt(QToPE_err**2 + IErr**2))

    fig,ax = plt.subplots()
    ax.bar(dates,date_sums,yerr=date_stdevs,alpha=0.5,color='purple',ecolor='black')
    ax.set_xlabel("Date") 
    ax.set_ylabel("Total Avg. PE per flash")
    plt.xticks(rotation='30',fontsize=12)
    plt.title(("Mean PE seen by all ETEL tubes per LED flash \n" +
        "LED 6 only (PIN 3500)"))
    plt.show()
    
    fig,ax = plt.subplots()
    for cnum in TUBES:
        myx = []
        myy = []
        myyerr = []
        for j,date in enumerate(data):
            myx.append(date)
            print("DATE IS: " + str(date))
            print("CHECK THIS")
            print(float(ndpd.loc[((ndpd["date"] == str(date)) & (ndpd["channel"] == cnum)), "PE"]))
            myy.append(float(ndpd.loc[((ndpd["date"] == str(date)) & (ndpd["channel"] == cnum)), "PE"])),
            myyerr.append(float(ndpd.loc[((ndpd["date"] == str(date)) & (ndpd["channel"] == cnum)), "PEUnc"]))
        ax.errorbar(myx,myy,yerr=myyerr,alpha=0.8,label=cnum,linestyle='None',marker='o',markersize=6)
        #ax.bar(y = myy,x = range(len(myx)), yerr = myyerr,label = cnum)
        #ax.xticks(range(len(myx)),myx)
    leg = ax.legend(loc=1,fontsize=15)
    leg.set_frame_on(True)
    leg.draw_frame(True)
    ax.set_xlabel("Date") 
    ax.set_ylabel("PEs") 
    plt.xticks(rotation='30',fontsize=10)
    plt.title(("Average PE seen per LED flash \n" +
        "LED 6 only (PIN 3500)"))
    plt.show()
