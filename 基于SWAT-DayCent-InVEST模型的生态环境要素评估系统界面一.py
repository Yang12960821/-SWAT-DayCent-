import os
import pandas as pd
import numpy as np
import sys
from sklearn.metrics import mean_squared_error, r2_score
from scipy import stats
from matplotlib import rcParams
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from pandas import Series,DataFrame
import geopandas as gp


def linear_fit(x,y):
	x_m=np.mean(x)
	y_m=np.mean(y)
	x1=(x-x_m)
	y1=y-y_m
	x2=sum((x-x_m)**2)
	xy=sum(x1*y1)
	#回归参数的最小二乘估计
	beta1=xy/x2
	beta0=y_m-beta1*x_m
	#方差
	sigma2=sum((y-beta0-beta1*x)**2)/(len(x))
	#标准差
	sigma=np.sqrt(sigma2)
	#求t值
	t=beta1*np.sqrt(x2)/sigma
	#已知临界值求p值
	p=stats.t.sf(t,len(x))
	p=stats.ttest_ind(x,y)[1]
	y_prd=beta0+beta1*np.array(x)
	Regression = np.sum((y_prd - np.mean(y))**2) # 回归平方和
	Residual  = sum((y - y_prd)**2)     # 残差平方和
	total = sum((y-np.mean(y))**2) #总体平方和
	R2  = 1-Residual / total # 相关性系数R^2
	#RMSE
	rmse=np.sqrt(mean_squared_error(x,y))
	#R2
	return beta1,beta0,p,R2,rmse,sigma
def d_bins(data):
    q = data.quantile([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9])
    bins=[np.min(data)]+list(q)+[np.max(data)]
    nbin = len(bins)-1
    return bins,nbin

#SWAT Model output analysis
#Read SWAT_DayCent output data,SWAT output_monthly data,DayCent output yearly data
#MON and area divided
def mon_area_split(data):
    mon_area = data.str.split('.',expand=True)
    df = mon_area.apply(pd.to_numeric, errors='coerce')
    return df
def read_SWAT_output_hru(folder_path):
    """get SWAT output.hru or output.sub or output.rch normal format
       get hru number
       get sub number
    """
    hru_path = folder_path+"/TxtInOut/output.hru"
    output_hru = pd.read_table(hru_path,skiprows = 9,sep ='\s+',header = None,dtype = str)
    hru_num = int(output_hru.iloc[-1,1]) #hru是第二列    
    output_hru = output_hru[:-hru_num]
    hru_df1 = output_hru.iloc[:,0:5]
    hru_df2 = mon_area_split(output_hru[:][5])
    hru_df3 = output_hru.iloc[:,6:]
    hru_df3 = hru_df3.apply(pd.to_numeric, errors='coerce')
    output_hru_df = pd.concat([hru_df1,hru_df2,hru_df3],axis = 1)
    output_hru_df.columns = ["LULC","HRU","GIS","SUB","MGT","MON","AREAkm2","PCP/mm","SNOFALL/mm","SNOMELT/mm","IRR/mm",
            "PET/mm","ET/mm","SW_INIT/mm","SW_END/mm","PERC/mm","GW_RCHG/mm","DA_RCHG/mm","REVAP/mm",
            "SA_IRR/mm","DA_IRR/mm","SA_ST/mm","DA_ST/mm","SURQ_GEN/mm","SURQ_CNT/mm","TLOSS/mm",
            "LATQGEN/mm","GW_Q/mm","WYLD/mm","DAILYCN","TMP_AV/dgC","TMP_MX/dgC","TMP_MN/dgC","SOL_TMP/dgC",
            "SOLAR/MJ/m2","SYLD/t/ha","USLE/t/ha","N_APP/kg/ha","P_APP/kg/ha","NAUTO/kg/ha","PAUTO/kg/ha", 
            "NGRZ/kg/ha","PGRZ/kg/ha","NCFRT/kg/ha","PCFRT/kg/ha","NRAINkg/ha","NFIX/kg/ha","F-MN/kg/ha",
            "A-MN/kg/ha","A-SN/kg/ha","F-MP/kg/ha","AO-LP/kg/ha","L-APkg/ha","A-SP/kg/ha","DNIT/kg/ha",
            "NUP/kg/ha","PUP/kg/ha","ORGN/kg/ha","ORGP/kg/ha","SEDP/kg/ha","NSURQ/kg/ha","NLATQ/kg/ha",
            "NO3L/kg/ha","NO3GW/kg/ha", "SOLP/kg/ha", "P_GW/kg/ha","W_STRS","TMP_STRS","N_STRS","P_STRS",
            "BIOM/t/ha","LAI","YLD/t/ha","BACTP/ct","BACTLP/ct","WTAB CLI/m","WTAB SOL/m","SNO/mm",
            "CMUP/kg/ha","CMTOT/kg/ha","QTILE/mm","TNO3/kg/ha","LNO3/kg/ha","GW_Q_D/mm","LATQCNT/mm"]
    return output_hru_df,hru_num
def read_SWAT_output_sub(folder_path):   
    sub_path = folder_path+"/TxtInOut/output.sub"
    output_sub = pd.read_table(sub_path,skiprows = 9,sep ='\s+',header = None,dtype = str)  
    sub_num = int(output_sub.iloc[-1,1])
    output_sub = output_sub.iloc[:-sub_num,1:]
    sub_df1 = output_sub.iloc[:,0:1]
    sub_df2 = mon_area_split(output_sub.iloc[:,2]) 
    sub_df3 = output_sub.iloc[:,3:]
    sub_df3 = sub_df3.apply(pd.to_numeric, errors='coerce')
    output_sub_df = pd.concat([sub_df1,sub_df2,sub_df3],axis = 1)
    output_sub_df.columns = ['SUB','MON','AREA m2','PCP/mm','SNOMELT/mm','PET/mm','ET/mm','SW/mm','PERC mm','SURQ/mm',
                             'GW_Q/mm','WYLD/mm','SYLD/t/ha','ORGN/kg/ha','ORGP/kg/ha','NSURQ/kg/ha', 'SOLP/kg/ha','SEDP/kg/ha',
                             'LAT Q/mm','LATNO3/kg/ha','GWNO3/kg/ha','CHOLA/mic/L','CBODU/mg/L','DOXQ/mg/L','TNO3/kg/ha']
    return output_sub_df,sub_num
def read_SWAT_output_rch(folder_path):    
    rch_path = folder_path+"/TxtInOut/output.rch"
    output_rch = pd.read_table(rch_path,skiprows = 9,sep ='\s+',header = None,dtype = str)
    rch_num = int(output_rch.iloc[-1,1])
    output_rch_df = output_rch.iloc[:-rch_num,1:]
    output_rch_df = output_rch_df.apply(pd.to_numeric, errors='coerce')
    output_rch_df.columns = ['RCH','GIS','MON','AREA km2','FLOW_IN/cms', 'FLOW_OUT/cms','EVAP/cms' ,'TLOSS/cms','SED_IN/tons','SED_OUT/tons',
                             'SEDCONC/mg/kg','ORGN_IN/kg','ORGN_OUT/kg','ORGP_IN/kg','ORGP_OUT/kg','NO3_IN/kg','NO3_OUT/kg','NH4_IN/kg','NH4_OUT/kg',
                             'NO2_IN/kg','NO2_OUT/kg' ,'MINP_IN/kg','MINP_OUT/kg','CHLA_IN/kg','CHLA_OUT/kg','CBOD_IN/kg','CBOD_OUT/kg','DISOX_IN/kg',
                             'DISOX_OUT/kg','SOLPST_IN/mg','SOLPST_OUT/mg ','SORPST_IN/mg','SORPST_OUT/mg','REACTPST/mg','VOLPST/mg','SETTLPST/mg',
                             'RESUSP_PST/mg','DIFFUSEPST/mg','REACBEDPST/mg','BURYPST/mg','BED_PST/mg', 'BACTP_OUT/ct','BACTLP_OUT/ct','CMETAL_1 kg',
                             'CMETAL_2/kg','CMETAL_3/kg','TOT N/kg','TOT P/kg', 'NO3CONC/Mg/l','WTMP/degc']
    return output_rch_df,rch_num

#Basin尺度，输出年、季节的时间变化图和年内分布情况的数据
def SWAT_output_basin(folder_path,begin_year,end_year,parameters_list,out_path,flag,time):
    output_hru_df,hru_num = read_SWAT_output_hru(folder_path)
    #根据hru的面积进行加权
    basin_area = np.sum(output_hru_df["AREAkm2"][:hru_num])
    output_hru_df["AREAkm2"] = output_hru_df["AREAkm2"]/basin_area
    if len(parameters_list)>1:
        for time_space in time:    
            # #年分析：
            if time_space == "year":
                year_seq = np.arange(begin_year,end_year+1 , 1)
                output_hru_year = output_hru_df[(output_hru_df['MON']<=end_year)&(output_hru_df['MON']>=begin_year)]
                HydroParameyers_y = pd.DataFrame()
                HydroParameyers_y['Year'] = year_seq
                for par in parameters_list:
                    output_hru_year[par] = output_hru_year["AREAkm2"]*output_hru_year[par]
                    par_y = pd.pivot_table(output_hru_year[['MON',par]],index=['MON'],values = par, aggfunc="sum")
                    HydroParameyers_y[par] = par_y[par].tolist()
                HydroParameyers_y.to_csv(out_path+'HydroParameter_Basin_Year.csv',sep=',',index=False,header=True)
                if flag ==1:
                    subplot_num = len(parameters_list)
                    fig,ax=plt.subplots(1,subplot_num,figsize=(4*subplot_num,3),sharex=False, sharey=False)
                    print('plotting basin year trend...')
                    for i in range(subplot_num):
                        year = HydroParameyers_y['Year']
                        par_y = HydroParameyers_y[parameters_list[i]]
                        beta1,beta0,p,R2,rmse,sigma = linear_fit(year,par_y)
                        if p<=0.05:
                            strp='$\it{p}$<=0.05'
                        else:
                            strp='$\it{p}$>0.05'
                        ax[i].plot(year,par_y,linestyle='-',linewidth=0.8,color='dimgray', marker='o',markersize='3',markeredgecolor='black',markeredgewidth=0.5,markerfacecolor='white')
                        ax[i].plot(year,year*beta1+beta0,linewidth=1,color='r',linestyle='--',zorder=1)
                        ax[i].set(xlim=(year[0]-5,year.tolist()[-1]+5))
                        ax[i].set(ylim=(0.8*np.min(par_y),1.2*np.max(par_y)))
                        ax[i].text(year[0],np.max(par_y),"y="+str(round(beta1,2))+'x'+str(round(beta0,2))+'    '+'$\it{R}$$^2$='+str(round(R2,2),)+
                                   '\n'+strp+'    '+'SD='+str(round(sigma,2)),fontsize=12,verticalalignment="bottom")
                        ax[i].set(ylabel = parameters_list[i])
                    plt.rcParams['font.size']=12
                    plt.rcParams['font.family']='arial'
                    plt.rcParams['xtick.labelsize']=12
                    plt.rcParams['ytick.labelsize']=12
                    plt.rcParams['xtick.major.pad']=8
                    plt.rcParams['ytick.major.pad']=8
                    plt.tight_layout()
                    plt.savefig(out_path+'HydroParameter_Basin_Year.tif',bbox_inches='tight',dpi=300)
            elif time_space == "month":
                #月分析
                row0 = output_hru_df[output_hru_df['MON']==begin_year].index[0]-12*hru_num
                row1 = output_hru_df[output_hru_df['MON']==end_year].index[0]
                output_hru_df_1 = output_hru_df.iloc[row0:row1,]
                output_hru_mon  = output_hru_df_1[output_hru_df_1["MON"]<=12]
                HydroParameyers_mon = pd.DataFrame()
                HydroParameyers_mon['Month'] = np.arange(1,13,1)
                for par in parameters_list:
                    output_hru_mon[par] = output_hru_mon["AREAkm2"]*output_hru_mon[par]
                    par_mon = pd.pivot_table(output_hru_mon,index=['HRU'],columns='MON',values=par, aggfunc="mean")
                    HydroParameyers_mon[par] = par_mon.sum().tolist()
                HydroParameyers_mon.to_csv(out_path+'HydroParameter_Basin_Month.csv',sep=',',index=False,header=True)
                if flag ==1:
                    print('plotting monthly distribution...')
                    HydroParameyers_mon.plot(x='Month', y=parameters_list, kind='line',marker='o',subplots=False,figsize = (4,3))
                    plt.ylim(0,np.max(np.max(HydroParameyers_mon[parameters_list]))*1.2)
                    plt.xticks(np.linspace(0,12,7,endpoint = True))
                    plt.xlabel('Month',fontsize = 14)
                    plt.rcParams['font.size']=12
                    plt.rcParams['font.family']='arial'
                    plt.rcParams['xtick.labelsize']=14
                    plt.rcParams['ytick.labelsize']=14
                    plt.rcParams['xtick.major.pad']=8
                    plt.rcParams['ytick.major.pad']=8
                    plt.legend(loc ='upper left',edgecolor = 'none',facecolor = 'none')
                    plt.savefig(out_path+'HydroParameter_Basin_Month.tif',bbox_inches='tight',dpi=300)
            elif time_space == "season":
                #季节分析
                year_seq = np.arange(begin_year,end_year+1 , 1)
                year = (hru_num*12*year_seq.tolist())
                year.sort(reverse = False)
                row0 = output_hru_df[output_hru_df['MON']==begin_year].index[0]-12*hru_num
                row1 = output_hru_df[output_hru_df['MON']==end_year].index[0]
                output_hru_df_1 = output_hru_df.iloc[row0:row1,]
                output_hru_mon  = output_hru_df_1[output_hru_df_1["MON"]<=12]
                output_hru_mon["YEAR"] = year
                HydroParameyers_season = pd.DataFrame()
                HydroParameyers_season['year'] = year_seq
                for par in parameters_list:
                    output_hru_mon[par] = output_hru_mon["AREAkm2"]*output_hru_mon[par]
                    par_mon_y = pd.pivot_table(output_hru_mon,index=['YEAR'],columns='MON',values=[par],aggfunc=[np.sum])
                    #这里需要加个判断，因为有些变量需要求平均值
                    if par == "SW_END/mm":
                        HydroParameyers_season[par+'_Spring'] = par_mon_y.iloc[:,[2,3,4]].apply(lambda x: x.mean(),axis=1).tolist()
                        HydroParameyers_season[par+'_Summer'] = par_mon_y.iloc[:,[5,6,7]].apply(lambda x: x.mean(),axis=1).tolist()
                        HydroParameyers_season[par+'_Autumn'] = par_mon_y.iloc[:,[8,9,10]].apply(lambda x: x.mean(),axis=1).tolist()
                        HydroParameyers_season[par+'_Winter'] = par_mon_y.iloc[:,[11,0,1]].apply(lambda x: x.mean(),axis=1).tolist()
                    else:
                        HydroParameyers_season[par+'_Spring'] = par_mon_y.iloc[:,[2,3,4]].apply(lambda x: x.sum(),axis=1).tolist()
                        HydroParameyers_season[par+'_Summer'] = par_mon_y.iloc[:,[5,6,7]].apply(lambda x: x.sum(),axis=1).tolist()
                        HydroParameyers_season[par+'_Autumn'] = par_mon_y.iloc[:,[8,9,10]].apply(lambda x: x.sum(),axis=1).tolist()
                        HydroParameyers_season[par+'_Winter'] = par_mon_y.iloc[:,[11,0,1]].apply(lambda x: x.sum(),axis=1).tolist()
                HydroParameyers_season.to_csv(out_path+'HydroParameter_Basin_Season.csv',sep=',',index=False,header=True)
                if flag == 1:
                    subplot_num = len(parameters_list)
                    fig,ax=plt.subplots(1,subplot_num,figsize=(4*subplot_num,3),sharex=False, sharey=False)
                    print('plotting Season year trend...')
                    for i in range(subplot_num):
                        year = HydroParameyers_season['year']
                        four_seasons = ['_Spring','_Summer','_Autumn','_Winter']
                        par_s = HydroParameyers_season[[parameters_list[i]+k for k in four_seasons]]
                        # colors = ['green','crimson','orange','dimgray']
                        l1, = ax[i].plot(year, par_s[parameters_list[i]+'_Spring'],linestyle='-',linewidth=0.8,color='green')
                        l2, = ax[i].plot(year, par_s[parameters_list[i]+'_Summer'],linestyle='-',linewidth=0.8,color='crimson')
                        l3, = ax[i].plot(year, par_s[parameters_list[i]+'_Autumn'],linestyle='-',linewidth=0.8,color='orange')
                        l4, = ax[i].plot(year, par_s[parameters_list[i]+'_Winter'],linestyle='-',linewidth=0.8,color='dimgray')
                        ax[i].legend(handles = [l1,l2,l3,l4] , labels=['Spring', 'Summer', 'Autumn','Winter'],loc = 'upper left',edgecolor = 'none',facecolor = 'none',fontsize = 10)
                        ax[i].set(xlim=(year[0]-5,year.tolist()[-1]+5))
                        ax[i].set(ylim=(0,1.5*np.max(np.max(par_s))))
                        for j in range(4):
                            x=year
                            y = par_s[parameters_list[i]+four_seasons[j]]
                            beta1,beta0,p,R2,rmse,sigma = linear_fit(x,y)
                            if p<=0.05:
                                strp='$\it{p}$<=0.05'
                            else:
                                strp='$\it{p}$>0.05'
                #           ax[i].plot(x, y,linestyle='-',linewidth=0.8,color=colors[j])
                            if beta0<0:
                                ax[i].text(year[0]+len(year)*0.3,1.5*np.max(np.max(par_s))-1.5*np.max(np.max(par_s))*0.09*(j+1),"y="+str(round(beta1,2))+'x'+str(round(beta0,2))+'    '+strp,fontsize=10)
                            else:
                                ax[i].text(year[0]+len(year)*0.3,1.5*np.max(np.max(par_s))-1.5*np.max(np.max(par_s))*0.09*(j+1),"y="+str(round(beta1,2))+'x+'+str(round(beta0,2))+'    '+strp,fontsize=10)
                    plt.rcParams['font.size']=12
                    plt.rcParams['font.family']='arial'
                    plt.rcParams['xtick.labelsize']=12
                    plt.rcParams['ytick.labelsize']=12
                    plt.rcParams['xtick.major.pad']=8
                    plt.rcParams['ytick.major.pad']=8
                    plt.tight_layout()     
                    plt.savefig(out_path+'HydroParameter_Basin_season.tif',bbox_inches='tight',dpi=300)
    if len(parameters_list)==1: 
        for time_space in time:    
            # #年分析：
            if time_space == "year":
                year_seq = np.arange(begin_year,end_year+1 , 1)
                output_hru_year = output_hru_df[(output_hru_df['MON']<=end_year)&(output_hru_df['MON']>=begin_year)]
                HydroParameyers_y = pd.DataFrame()
                HydroParameyers_y['Year'] = year_seq
                for par in parameters_list:
                    output_hru_year[par] = output_hru_year["AREAkm2"]*output_hru_year[par]
                    par_y = pd.pivot_table(output_hru_year[['MON',par]],index=['MON'],values = par, aggfunc="sum")
                    HydroParameyers_y[par] = par_y[par].tolist()
                HydroParameyers_y.to_csv(out_path+'HydroParameter_Basin_Year.csv',sep=',',index=False,header=True)
                if flag ==1:
                    subplot_num = len(parameters_list)
                    fig,ax=plt.subplots(figsize=(4,3),sharex=False, sharey=False)
                    print('plotting basin year trend...')
                    year = HydroParameyers_y['Year']
                    par_y = HydroParameyers_y[parameters_list[0]]
                    beta1,beta0,p,R2,rmse,sigma = linear_fit(year,par_y)
                    if p<=0.05:
                        strp='$\it{p}$<=0.05'
                    else:
                        strp='$\it{p}$>0.05'
                    ax.plot(year,par_y,linestyle='-',linewidth=0.8,color='dimgray', marker='o',markersize='3',markeredgecolor='black',markeredgewidth=0.5,markerfacecolor='white')
                    ax.plot(year,year*beta1+beta0,linewidth=1,color='r',linestyle='--',zorder=1)
                    ax.set(xlim=(year[0]-5,year.tolist()[-1]+5))
                    ax.set(ylim=(0.8*np.min(par_y),1.2*np.max(par_y)))
                    ax.text(year[0],np.max(par_y),"y="+str(round(beta1,2))+'x'+str(round(beta0,2))+'    '+'$\it{R}$$^2$='+str(round(R2,2),)+
                               '\n'+strp+'    '+'SD='+str(round(sigma,2)),fontsize=12,verticalalignment="bottom")
                    ax.set(ylabel = parameters_list[0])
                    plt.rcParams['font.size']=12
                    plt.rcParams['font.family']='arial'
                    plt.rcParams['xtick.labelsize']=12
                    plt.rcParams['ytick.labelsize']=12
                    plt.rcParams['xtick.major.pad']=8
                    plt.rcParams['ytick.major.pad']=8
                    plt.tight_layout()
                    plt.savefig(out_path+'HydroParameter_Basin_Year.tif',bbox_inches='tight',dpi=300)
            elif time_space == "month":
                #月分析
                row0 = output_hru_df[output_hru_df['MON']==begin_year].index[0]-12*hru_num
                row1 = output_hru_df[output_hru_df['MON']==end_year].index[0]
                output_hru_df_1 = output_hru_df.iloc[row0:row1,]
                output_hru_mon  = output_hru_df_1[output_hru_df_1["MON"]<=12]
                HydroParameyers_mon = pd.DataFrame()
                HydroParameyers_mon['Month'] = np.arange(1,13,1)
                par = parameters_list[0]
                output_hru_mon[par] = output_hru_mon["AREAkm2"]*output_hru_mon[par]
                par_mon = pd.pivot_table(output_hru_mon,index=['HRU'],columns='MON',values=par, aggfunc="mean")
                HydroParameyers_mon[par] = par_mon.sum().tolist()
                HydroParameyers_mon.to_csv(out_path+'HydroParameter_Basin_Month.csv',sep=',',index=False,header=True)
                if flag ==1:
                    print('plotting monthly distribution...')
                    HydroParameyers_mon.plot(x='Month', y=parameters_list, kind='line',marker='o',subplots=False,figsize = (4,3))
                    plt.ylim(0,np.max(np.max(HydroParameyers_mon[parameters_list]))*1.2)
                    plt.xticks(np.linspace(0,12,7,endpoint = True))
                    plt.xlabel('Month',fontsize = 14)
                    plt.rcParams['font.size']=12
                    plt.rcParams['font.family']='arial'
                    plt.rcParams['xtick.labelsize']=14
                    plt.rcParams['ytick.labelsize']=14
                    plt.rcParams['xtick.major.pad']=8
                    plt.rcParams['ytick.major.pad']=8
                    plt.legend(loc ='upper left',edgecolor = 'none',facecolor = 'none')
                    plt.savefig(out_path+'HydroParameter_Basin_Month.tif',bbox_inches='tight',dpi=300)
            elif time_space == "season":
                #季节分析
                year_seq = np.arange(begin_year,end_year+1 , 1)
                year = (hru_num*12*year_seq.tolist())
                year.sort(reverse = False)
                row0 = output_hru_df[output_hru_df['MON']==begin_year].index[0]-12*hru_num
                row1 = output_hru_df[output_hru_df['MON']==end_year].index[0]
                output_hru_df_1 = output_hru_df.iloc[row0:row1,]
                output_hru_mon  = output_hru_df_1[output_hru_df_1["MON"]<=12]
                output_hru_mon["YEAR"] = year
                HydroParameyers_season = pd.DataFrame()
                HydroParameyers_season['year'] = year_seq
                par = parameters_list[0]
                output_hru_mon[par] = output_hru_mon["AREAkm2"]*output_hru_mon[par]
                par_mon_y = pd.pivot_table(output_hru_mon,index=['YEAR'],columns='MON',values=[par],aggfunc=[np.sum])
                #这里需要加个判断，因为有些变量需要求平均值
                if par == "SW_END/mm":
                    HydroParameyers_season[par+'_Spring'] = par_mon_y.iloc[:,[2,3,4]].apply(lambda x: x.mean(),axis=1).tolist()
                    HydroParameyers_season[par+'_Summer'] = par_mon_y.iloc[:,[5,6,7]].apply(lambda x: x.mean(),axis=1).tolist()
                    HydroParameyers_season[par+'_Autumn'] = par_mon_y.iloc[:,[8,9,10]].apply(lambda x: x.mean(),axis=1).tolist()
                    HydroParameyers_season[par+'_Winter'] = par_mon_y.iloc[:,[11,0,1]].apply(lambda x: x.mean(),axis=1).tolist()
                else:
                    HydroParameyers_season[par+'_Spring'] = par_mon_y.iloc[:,[2,3,4]].apply(lambda x: x.sum(),axis=1).tolist()
                    HydroParameyers_season[par+'_Summer'] = par_mon_y.iloc[:,[5,6,7]].apply(lambda x: x.sum(),axis=1).tolist()
                    HydroParameyers_season[par+'_Autumn'] = par_mon_y.iloc[:,[8,9,10]].apply(lambda x: x.sum(),axis=1).tolist()
                    HydroParameyers_season[par+'_Winter'] = par_mon_y.iloc[:,[11,0,1]].apply(lambda x: x.sum(),axis=1).tolist()
                HydroParameyers_season.to_csv(out_path+'HydroParameter_Basin_Season.csv',sep=',',index=False,header=True)
                if flag == 1:
                    fig,ax=plt.subplots(figsize=(4,3),sharex=False, sharey=False)
                    print('plotting Season year trend...')
                    year = HydroParameyers_season['year']
                    four_seasons = ['_Spring','_Summer','_Autumn','_Winter']
                    par_s = HydroParameyers_season[[parameters_list[0]+k for k in four_seasons]]
                    l1, = ax.plot(year, par_s[parameters_list[0]+'_Spring'],linestyle='-',linewidth=0.8,color='green')
                    l2, = ax.plot(year, par_s[parameters_list[0]+'_Summer'],linestyle='-',linewidth=0.8,color='crimson')
                    l3, = ax.plot(year, par_s[parameters_list[0]+'_Autumn'],linestyle='-',linewidth=0.8,color='orange')
                    l4, = ax.plot(year, par_s[parameters_list[0]+'_Winter'],linestyle='-',linewidth=0.8,color='dimgray')
                    ax.legend(handles = [l1,l2,l3,l4] , labels=['Spring', 'Summer', 'Autumn','Winter'],loc = 'upper left',edgecolor = 'none',facecolor = 'none',fontsize = 10)
                    ax.set(xlim=(year[0]-5,year.tolist()[-1]+5))
                    ax.set(ylim=(0,1.5*np.max(np.max(par_s))))
                    for j in range(4):
                        x=year
                        y = par_s[parameters_list[0]+four_seasons[j]]
                        beta1,beta0,p,R2,rmse,sigma = linear_fit(x,y)
                        if p<=0.05:
                            strp='$\it{p}$<=0.05'
                        else:
                            strp='$\it{p}$>0.05'
            #           ax[i].plot(x, y,linestyle='-',linewidth=0.8,color=colors[j])
                        if beta0<0:
                            ax.text(year[0]+len(year)*0.3,1.5*np.max(np.max(par_s))-1.5*np.max(np.max(par_s))*0.09*(j+1),"y="+str(round(beta1,2))+'x'+str(round(beta0,2))+'    '+strp,fontsize=10)
                        else:
                            ax.text(year[0]+len(year)*0.3,1.5*np.max(np.max(par_s))-1.5*np.max(np.max(par_s))*0.09*(j+1),"y="+str(round(beta1,2))+'x+'+str(round(beta0,2))+'    '+strp,fontsize=10)
                    plt.rcParams['font.size']=12
                    plt.rcParams['font.family']='arial'
                    plt.rcParams['xtick.labelsize']=12
                    plt.rcParams['ytick.labelsize']=12
                    plt.rcParams['xtick.major.pad']=8
                    plt.rcParams['ytick.major.pad']=8
                    plt.tight_layout()     
                    plt.savefig(out_path+'HydroParameter_Basin_season.tif',bbox_inches='tight',dpi=300)
                    
# SWAT output land use statistical
def SWAT_lulc_year(folder_path,begin_year,end_year,parameters_list,out_path):
    output_hru_df,hru_num = read_SWAT_output_hru(folder_path)
    output_hru_year = output_hru_df[(output_hru_df['MON']<=end_year)&(output_hru_df['MON']>=begin_year)]
    Pars_lulc_ny_mean = pd.DataFrame()
    for par in parameters_list:
        par_lulc_y = pd.pivot_table(output_hru_year,index=['MON'],columns='LULC',values= par ,aggfunc=[np.mean])
        par_lulc_y.columns = [i[1] for i in par_lulc_y.columns]
        par_name = par.split('/')[0]
        par_lulc_y.to_csv(out_path+par_name+'_lulc_year.csv',sep=',',index=True,header=True)
        Pars_lulc_ny_mean[par_name] = np.mean(par_lulc_y)
    Pars_lulc_ny_mean.to_csv(out_path+'HydrosPars_lulc_ny_mean.csv',sep=',',index=True,header=True) 
    Pars_lulc_ny_mean[:-1].plot(use_index=True, kind='bar',subplots=False,figsize = (4,3))
    plt.rcParams['font.size']=12
    plt.rcParams['font.family']='arial'
    plt.rcParams['xtick.labelsize']=14
    plt.rcParams['ytick.labelsize']=14
    plt.rcParams['xtick.major.pad']=8
    plt.rcParams['ytick.major.pad']=8
    plt.legend(loc ='upper left',edgecolor = 'none',facecolor = 'none')
    plt.savefig(out_path+'HydroPars_lulc_ny_mean.tif',bbox_inches='tight',dpi=300) 
    
#SUB尺度上的分析（空间分布和空间趋势）
def SWAT_sub_space_data(folder_path,begin_year,end_year,parameters_list,out_path,flag):
    output_sub_df,sub_num = read_SWAT_output_sub(folder_path)
    output_sub_year = output_sub_df[(output_sub_df['MON']<=end_year)&(output_sub_df['MON']>=begin_year)]
    Pars_sub_mean_slope = pd.DataFrame()
    Pars_sub_mean_slope["Subbasin"] = np.arange(1,sub_num+1,1)
    for par in parameters_list:
        par_year_sub = pd.pivot_table(output_sub_year,index=['SUB'],columns='MON',values= par ,aggfunc=[np.mean])
        par_name = par.split('/')[0]
        par_year_sub[par_name+"_ymean"] = par_year_sub.iloc[:,:].apply(lambda x: x.mean(),axis=1)
        par_year_sub_trend = []
        for sub in range(sub_num):
            beta1,beta0,p,R2,rmse,sigma = linear_fit(range(begin_year,end_year+1,1),par_year_sub.iloc[sub,:-1].values)
            par_year_sub_trend.append(beta1)
        par_year_sub[par_name+"_yslope"] = par_year_sub_trend
        #增加HRU_ID一列
        index_num = [int(i) for i in par_year_sub.index]
        par_year_sub['Subbasin'] = index_num
        #colnames重置
        year_list = np.arange(begin_year, end_year+1 , 1).tolist()
        par_col_name = [par_name+"_"+str(i) for i in year_list]
        par_col_name.extend([ par_name+"_ymean",par_name+"_yslope","Subbasin"])
        par_year_sub.columns = par_col_name
        par_year_sub = par_year_sub.sort_values(by='Subbasin')
        par_sub = par_year_sub[[par_name+"_ymean",par_name+"_yslope","Subbasin"]]
        Pars_sub_mean_slope = Pars_sub_mean_slope.merge(par_sub,on = 'Subbasin', how = 'left')
        par_year_sub.to_csv(out_path+par_name+'_year_sub.csv',sep=',',index=False,header=True)
    Pars_sub_mean_slope.to_csv(out_path+'HydroParameter_Sub_mean_slope.csv',sep=',',index=False,header=True)
    if flag==1:
        data = Pars_sub_mean_slope
        data_geod = gp.GeoDataFrame(data)
        sub_shp = folder_path+"/Watershed/Shapes/subs1.shp"
        sub_geom  = gp.GeoDataFrame.from_file(sub_shp, encoding = 'gb18030')
        sub_data = sub_geom.merge(data_geod, on = 'Subbasin', how = 'left')
        subplot_row = len(parameters_list)
        fig,ax=plt.subplots(nrows=subplot_row, ncols=2,figsize=(6*2,4*subplot_row),sharex=False,sharey=False)
        print('plotting sub space distribution...')
        if subplot_row ==1:
            par = parameters_list[0].split('/')[0]
            unit = parameters_list[0].split('/')[1]
            if len(parameters_list[0].split('/'))==3:
                unit1 = parameters_list[0].split('/')[2]
            else:
                unit1 = ""
            bins1,nbin1 = d_bins(data[par+"_ymean"])
            bins1 = np.round(bins1,0)
            cmap1 = cm.get_cmap('Spectral', nbin1)
            norm1 = mcolors.BoundaryNorm(bins1, nbin1)
            sub_data.plot(par+"_ymean",ax = ax[0], k=12,norm  = norm1,cmap = cmap1)
            ax[0].axis('off')
            im1 = cm.ScalarMappable(norm=norm1, cmap= cmap1)
            cbar1 = fig.colorbar(
                im1, ax=ax[0], orientation='horizontal',
                shrink=0.5,pad = 0,
                label= parameters_list[0]
                )

            bins2,nbin2 = d_bins(data[par+"_yslope"])
            bins2 = np.round(bins2,1)
            cmap2 = cm.get_cmap('PiYG', nbin2)
            norm2 = mcolors.BoundaryNorm(bins2, nbin2)
            sub_data.plot(par+"_yslope",ax = ax[1], k=12,norm  = norm2,cmap = cmap2)
            ax[1].axis('off')
            im2 = cm.ScalarMappable(norm=norm2, cmap= cmap2)
            cbar2 = fig.colorbar(
                im2, ax=ax[1], orientation='horizontal',
                shrink=0.5,pad = 0,
                label= par+" trend "+unit+"/"+unit1+" y"
                )

            plt.rcParams['font.size']=12
            plt.rcParams['font.family']='arial'
            plt.subplots_adjust(wspace=-0.15,hspace=0)
            plt.savefig(out_path+'HydroParameter_Sub_distribution.tif',bbox_inches='tight',dpi=300)
        else:     
            for i in range(subplot_row):
                par = parameters_list[i].split('/')[0]
                unit = parameters_list[i].split('/')[1]
                if len(parameters_list[i].split('/'))==3:
                    unit1 = parameters_list[i].split('/')[2]
                else:
                    unit1 = ""
                bins1,nbin1 = d_bins(data[par+"_ymean"])
                bins1 = np.round(bins1,0)
                cmap1 = cm.get_cmap('Spectral', nbin1)
                norm1 = mcolors.BoundaryNorm(bins1, nbin1)
                sub_data.plot(par+"_ymean",ax = ax[i][0], k=12,norm  = norm1,cmap = cmap1)
                ax[i][0].axis('off')
                im1 = cm.ScalarMappable(norm=norm1, cmap= cmap1)
                cbar1 = fig.colorbar(
                    im1, ax=ax[i][0], orientation='horizontal',
                    shrink=0.5,pad = 0,
                    label= parameters_list[i]
                    )

                bins2,nbin2 = d_bins(data[par+"_yslope"])
                bins2 = np.round(bins2,1)
                cmap2 = cm.get_cmap('PiYG', nbin2)
                norm2 = mcolors.BoundaryNorm(bins2, nbin2)
                sub_data.plot(par+"_yslope",ax = ax[i][1], k=12,norm  = norm2,cmap = cmap2)
                ax[i][1].axis('off')
                im2 = cm.ScalarMappable(norm=norm2, cmap= cmap2)
                cbar2 = fig.colorbar(
                    im2, ax=ax[i][1], orientation='horizontal',
                    shrink=0.5,pad = 0,
                    label= par+" trend "+unit+"/"+unit1+" y"
                    )

            plt.rcParams['font.size']=12
            plt.rcParams['font.family']='arial'
            plt.subplots_adjust(wspace=-0.15,hspace=0.1)
            plt.savefig(out_path+'HydroParameter_Sub_distribution.tif',bbox_inches='tight',dpi=300)   
            
def SWAT_hru_space_data(folder_path,begin_year,end_year,parameters_list,out_path,flag):
    output_hru_df,hru_num = read_SWAT_output_hru(folder_path)
    output_hru_year = output_hru_df[(output_hru_df['MON']<=end_year)&(output_hru_df['MON']>=begin_year)]
    Pars_hru_mean_slope = pd.DataFrame()
    Pars_hru_mean_slope["HRU_ID"] = np.arange(1,hru_num+1,1)
    for par in parameters_list:
        par_year_hru = pd.pivot_table(output_hru_year,index=['HRU'],columns='MON',values= par ,aggfunc=[np.mean])
        par_name = par.split('/')[0]
        par_year_hru[par_name+"_ymean"] = par_year_hru.iloc[:,:].apply(lambda x: x.mean(),axis=1)
        par_year_hru_trend = []
        for hru in range(hru_num):
            beta1,beta0,p,R2,rmse,sigma = linear_fit(range(begin_year,end_year+1,1),par_year_hru.iloc[hru,:-1].values)
            par_year_hru_trend.append(beta1)
        par_year_hru[par_name+"_yslope"] = par_year_hru_trend
        #增加HRU_ID一列
        index_num = [int(i) for i in par_year_hru.index]
        par_year_hru['HRU_ID'] = index_num
        #colnames重置
        year_list = np.arange(begin_year, end_year+1 , 1).tolist()
        par_col_name = [par_name+"_"+str(i) for i in year_list]
        par_col_name.extend([ par_name+"_ymean",par_name+"_yslope","HRU_ID"])
        par_year_hru.columns = par_col_name
        par_year_hru = par_year_hru.sort_values(by='HRU_ID')
        par_hru = par_year_hru[[par_name+"_ymean",par_name+"_yslope","HRU_ID"]]
        Pars_hru_mean_slope = Pars_hru_mean_slope.merge(par_hru,on = 'HRU_ID', how = 'left')
        par_year_hru.to_csv(out_path+par_name+'_year_hru.csv',sep=',',index=False,header=True)
    Pars_hru_mean_slope.to_csv(out_path+'HydroParameter_Hru_mean_slope.csv',sep=',',index=False,header=True)
    if flag ==1:
        data = Pars_hru_mean_slope
        data_geod = gp.GeoDataFrame(data)
        hru_shp=folder_path+"/Watershed/Shapes/hru1.shp"
        hru_geom  = gp.GeoDataFrame.from_file(hru_shp, encoding = 'gb18030')
        hru_data = hru_geom.merge(data_geod, on = 'HRU_ID', how = 'left')
        subplot_row = len(parameters_list)
        fig,ax=plt.subplots(nrows=subplot_row, ncols=2,figsize=(6*2,4*subplot_row),sharex=False,sharey=False)
        print('plotting hru space distribution...')
        if subplot_row ==1:
            par = parameters_list[0].split('/')[0]
            unit = parameters_list[0].split('/')[1]
            if len(parameters_list[0].split('/'))==3:
                unit1 = parameters_list[0].split('/')[2]
            else:
                unit1 = ""
            bins1,nbin1 = d_bins(data[par+"_ymean"])
            bins1 = np.round(bins1,0)
            cmap1 = cm.get_cmap('Spectral', nbin1)
            norm1 = mcolors.BoundaryNorm(bins1, nbin1)
            hru_data.plot(par+"_ymean",ax = ax[0], k=12,norm  = norm1,cmap = cmap1)
            ax[0].axis('off')
            im1 = cm.ScalarMappable(norm=norm1, cmap= cmap1)
            cbar1 = fig.colorbar(
                im1, ax=ax[0], orientation='horizontal',
                shrink=0.5,pad = 0,
                label= parameters_list[0]
                )

            bins2,nbin2 = d_bins(data[par+"_yslope"])
            bins2 = np.round(bins2,1)
            cmap2 = cm.get_cmap('PiYG', nbin2)
            norm2 = mcolors.BoundaryNorm(bins2, nbin2)
            hru_data.plot(par+"_yslope",ax = ax[1], k=12,norm  = norm2,cmap = cmap2)
            ax[1].axis('off')
            im2 = cm.ScalarMappable(norm=norm2, cmap= cmap2)
            cbar2 = fig.colorbar(
                im2, ax=ax[1], orientation='horizontal',
                shrink=0.5,pad = 0,
                label= par+" trend "+unit+"/"+unit1+" y"
                )

            plt.rcParams['font.size']=12
            plt.rcParams['font.family']='arial'
            plt.subplots_adjust(wspace=-0.15,hspace=0)
            plt.savefig(out_path+'HydroParameter_Hru_distribution.tif',bbox_inches='tight',dpi=300)
        else:            
            for i in range(subplot_row):
                par = parameters_list[i].split('/')[0]
                unit = parameters_list[i].split('/')[1]
                if len(parameters_list[i].split('/'))==3:
                    unit1 = parameters_list[i].split('/')[2]
                else:
                    unit1 = ""
                bins1,nbin1 = d_bins(data[par+"_ymean"])
                bins1 = np.round(bins1,0)
                cmap1 = cm.get_cmap('Spectral', nbin1)
                norm1 = mcolors.BoundaryNorm(bins1, nbin1)
                hru_data.plot(par+"_ymean",ax = ax[i][0], k=12,norm  = norm1,cmap = cmap1)
                ax[i][0].axis('off')
                im1 = cm.ScalarMappable(norm=norm1, cmap= cmap1)
                cbar1 = fig.colorbar(
                    im1, ax=ax[i][0], orientation='horizontal',
                    shrink=0.5,pad = 0,
                    label= parameters_list[i]
                    )

                bins2,nbin2 = d_bins(data[par+"_yslope"])
                bins2 = np.round(bins2,1)
                cmap2 = cm.get_cmap('PiYG', nbin2)
                norm2 = mcolors.BoundaryNorm(bins2, nbin2)
                hru_data.plot(par+"_yslope",ax = ax[i][1], k=12,norm  = norm2,cmap = cmap2)
                ax[i][1].axis('off')
                im2 = cm.ScalarMappable(norm=norm2, cmap= cmap2)
                cbar2 = fig.colorbar(
                    im2, ax=ax[i][1], orientation='horizontal',
                    shrink=0.5,pad = 0,
                    label= par+" trend "+unit+"/"+unit1+" y"
                    )
                
            plt.rcParams['font.size']=12
            plt.rcParams['font.family']='arial'
            plt.subplots_adjust(wspace=-0.15,hspace=0.1)
            plt.savefig(out_path+'HydroParameter_Hru_distribution.tif',bbox_inches='tight',dpi=300)
            
#SUB尺度上的分析（空间分布和空间趋势）
def SWAT_rch_space_data(folder_path,begin_year,end_year,parameters_list,out_path,flag):
    output_rch_df,rch_num = read_SWAT_output_rch(folder_path)
    output_rch_year = output_rch_df[(output_rch_df['MON']<=end_year)&(output_rch_df['MON']>=begin_year)]
    Pars_rch_mean_slope = pd.DataFrame()
    Pars_rch_mean_slope["Subbasin"] = np.arange(1,rch_num+1,1)
    for par in parameters_list:
        par_year_rch = pd.pivot_table(output_rch_year,index=['RCH'],columns='MON',values= par ,aggfunc=[np.mean])
        par_name = par.split('/')[0]
        par_year_rch[par_name+"_ymean"] = par_year_rch.iloc[:,:].apply(lambda x: x.mean(),axis=1)
        par_year_rch_trend = []
        for rch in range(rch_num):
            beta1,beta0,p,R2,rmse,sigma = linear_fit(range(begin_year,end_year+1,1),par_year_rch.iloc[rch,:-1].values)
            par_year_rch_trend.append(beta1)
        par_year_rch[par_name+"_yslope"] = par_year_rch_trend
        #增加HRU_ID一列
        index_num = [int(i) for i in par_year_rch.index]
        par_year_rch['Subbasin'] = index_num
        #colnames重置
        year_list = np.arange(begin_year, end_year+1 , 1).tolist()
        par_col_name = [par_name+"_"+str(i) for i in year_list]
        par_col_name.extend([ par_name+"_ymean",par_name+"_yslope","Subbasin"])
        par_year_rch.columns = par_col_name
        par_year_rch = par_year_rch.sort_values(by='Subbasin')
        par_rch = par_year_rch[[par_name+"_ymean",par_name+"_yslope","Subbasin"]]
        Pars_rch_mean_slope = Pars_rch_mean_slope.merge(par_rch,on = 'Subbasin', how = 'left')
        par_year_rch.to_csv(out_path+par_name+'_year_rch.csv',sep=',',index=False,header=True)
    Pars_rch_mean_slope.to_csv(out_path+'HydroParameter_rch_mean_slope.csv',sep=',',index=False,header=True)
    if flag==1:
        data = Pars_rch_mean_slope
        data_geod = gp.GeoDataFrame(data)
        sub_shp = folder_path+"/Watershed/Shapes/subs1.shp"
        sub_geom  = gp.GeoDataFrame.from_file(sub_shp, encoding = 'gb18030')
        rch_data = sub_geom.merge(data_geod, on = 'Subbasin', how = 'left')
        subplot_row = len(parameters_list)
        fig,ax=plt.subplots(nrows=subplot_row, ncols=2,figsize=(6*2,4*subplot_row),sharex=False,sharey=False)
        print('plotting rch space distribution...')
        if subplot_row ==1:
            par = parameters_list[0].split('/')[0]
            unit = parameters_list[0].split('/')[1]
            if len(parameters_list[0].split('/'))==3:
                unit1 = parameters_list[0].split('/')[2]
            else:
                unit1 = ""
            bins1,nbin1 = d_bins(data[par+"_ymean"])
            bins1 = np.round(bins1,2)
            cmap1 = cm.get_cmap('Spectral', nbin1)
            norm1 = mcolors.BoundaryNorm(bins1, nbin1)
            rch_data.plot(par+"_ymean",ax = ax[0], k=12,norm  = norm1,cmap = cmap1)
            ax[0].axis('off')
            im1 = cm.ScalarMappable(norm=norm1, cmap= cmap1)
            cbar1 = fig.colorbar(
                im1, ax=ax[0], orientation='horizontal',
                shrink=0.5,pad = 0,
                label= parameters_list[0]
                )

            bins2,nbin2 = d_bins(data[par+"_yslope"])
            bins2 = np.round(bins2,3)
            cmap2 = cm.get_cmap('PiYG', nbin2)
            norm2 = mcolors.BoundaryNorm(bins2, nbin2)
            rch_data.plot(par+"_yslope",ax = ax[1], k=12,norm  = norm2,cmap = cmap2)
            ax[1].axis('off')
            im2 = cm.ScalarMappable(norm=norm2, cmap= cmap2)
            cbar2 = fig.colorbar(
                im2, ax=ax[1], orientation='horizontal',
                shrink=0.5,pad = 0,
                label= par+" trend "+unit+"/"+unit1+" y"
                )

            plt.rcParams['font.size']=12
            plt.rcParams['font.family']='arial'
            plt.subplots_adjust(wspace=-0.15,hspace=0)
            plt.savefig(out_path+'HydroParameter_rch_distribution.tif',bbox_inches='tight',dpi=300)
        else:     
            for i in range(subplot_row):
                par = parameters_list[i].split('/')[0]
                unit = parameters_list[i].split('/')[1]
                if len(parameters_list[i].split('/'))==3:
                    unit1 = parameters_list[i].split('/')[2]
                else:
                    unit1 = ""
                bins1,nbin1 = d_bins(data[par+"_ymean"])
                bins1 = np.round(bins1,2)
                cmap1 = cm.get_cmap('Spectral', nbin1)
                norm1 = mcolors.BoundaryNorm(bins1, nbin1)
                rch_data.plot(par+"_ymean",ax = ax[i][0], k=12,norm  = norm1,cmap = cmap1)
                ax[i][0].axis('off')
                im1 = cm.ScalarMappable(norm=norm1, cmap= cmap1)
                cbar1 = fig.colorbar(
                    im1, ax=ax[i][0], orientation='horizontal',
                    shrink=0.5,pad = 0,
                    label= parameters_list[i]
                    )

                bins2,nbin2 = d_bins(data[par+"_yslope"])
                bins2 = np.round(bins2,3)
                cmap2 = cm.get_cmap('PiYG', nbin2)
                norm2 = mcolors.BoundaryNorm(bins2, nbin2)
                rch_data.plot(par+"_yslope",ax = ax[i][1], k=12,norm  = norm2,cmap = cmap2)
                ax[i][1].axis('off')
                im2 = cm.ScalarMappable(norm=norm2, cmap= cmap2)
                cbar2 = fig.colorbar(
                    im2, ax=ax[i][1], orientation='horizontal',
                    shrink=0.5,pad = 0,
                    label= par+" trend "+unit+"/"+unit1+" y"
                    )

            plt.rcParams['font.size']=12
            plt.rcParams['font.family']='arial'
            plt.subplots_adjust(wspace=-0.15,hspace=0.1)
            plt.savefig(out_path+'HydroParameter_rch_distribution.tif',bbox_inches='tight',dpi=300)  
            
#DayCent Model output analysis
def read_DayCent_output(folder_path):    
    CENT_output_path = folder_path+"/TxtInOut/CENT/CENT_year.out"
    CENT_output_data = pd.read_table(CENT_output_path,sep ='\s+')
    hru_num = CENT_output_data["iHRU"].tolist()[-1]
    sub_num = CENT_output_data["iSUB"].tolist()[-1]
    return CENT_output_data,hru_num,sub_num
#Basin尺度，输出年、季节的时间变化图和年内分布情况的数据
def Cent_output_basin(folder_path,begin_year,end_year,parameters_list,out_path,flag):
    CENT_output_data,hru_num,sub_num = read_DayCent_output(folder_path)
    #根据hru的面积进行加权
    #output_hru_df[:,7:] = output_hru_df[:,7:]*output_hru_df["AREAkm2"]/np.sum(output_hru_df["AREAkm2"][:hru_num])
    #年分析：
    year_seq = np.arange(begin_year,end_year+1 , 1)
    CENT_hru_year = CENT_output_data[(CENT_output_data['Y']<=end_year)&(CENT_output_data['Y']>=begin_year)]
    EcoParameyers_y = pd.DataFrame()
    EcoParameyers_y['Year'] = year_seq
    for par in parameters_list:
        par_y = pd.pivot_table(CENT_hru_year[['Y',par]],index=['Y'],values = par, aggfunc="mean")
        EcoParameyers_y[par] = par_y[par].tolist()
    EcoParameyers_y.to_csv(out_path+'EcoParameter_Basin_Year.csv',sep=',',index=False,header=True)
    
    if flag ==1:
        subplot_num = len(parameters_list)
        fig,ax=plt.subplots(1,subplot_num,figsize=(4*subplot_num,3),sharex=False, sharey=False)
        print('plotting basin year trend...')
        if subplot_num ==1:
            year = EcoParameyers_y['Year']
            par_y = EcoParameyers_y[parameters_list[0]]
            beta1,beta0,p,R2,rmse,sigma = linear_fit(year,par_y)
            if p<=0.05:
                strp='$\it{p}$<=0.05'
            else:
                strp='$\it{p}$>0.05'
            ax.plot(year,par_y,linestyle='-',linewidth=0.8,color='dimgray', marker='o',markersize='3',markeredgecolor='black',markeredgewidth=0.5,markerfacecolor='white')
            ax.plot(year,year*beta1+beta0,linewidth=1,color='r',linestyle='--',zorder=1)
            ax.set(xlim=(year[0]-5,year.tolist()[-1]+5))
            ax.set(ylim=(0.8*np.min(par_y),1.2*np.max(par_y)))
            ax.text(year[0],np.max(par_y),"y="+str(round(beta1,2))+'x'+str(round(beta0,2))+'    '+'$\it{R}$$^2$='+str(round(R2,2))+'\n'+strp+'    '+'SD='+str(round(sigma,2)),fontsize=12) 
            ax.set(ylabel = parameters_list[0])
            plt.rcParams['font.size']=12
            plt.rcParams['font.family']='arial'
            plt.rcParams['xtick.labelsize']=12
            plt.rcParams['ytick.labelsize']=12
            plt.rcParams['xtick.major.pad']=8
            plt.rcParams['ytick.major.pad']=8
            plt.tight_layout()    
            plt.savefig(out_path+'EcoParameter_Basin_Year.tif',bbox_inches='tight',dpi=300)
        else:
            for i in range(subplot_num):
                year = EcoParameyers_y['Year']
                par_y = EcoParameyers_y[parameters_list[i]]
                beta1,beta0,p,R2,rmse,sigma = linear_fit(year,par_y)
                if p<=0.05:
                    strp='$\it{p}$<=0.05'
                else:
                    strp='$\it{p}$>0.05'
                ax[i].plot(year,par_y,linestyle='-',linewidth=0.8,color='dimgray', marker='o',markersize='3',markeredgecolor='black',markeredgewidth=0.5,markerfacecolor='white')
                ax[i].plot(year,year*beta1+beta0,linewidth=1,color='r',linestyle='--',zorder=1)
                ax[i].set(xlim=(year[0]-5,year.tolist()[-1]+5))
                ax[i].set(ylim=(0.8*np.min(par_y),1.2*np.max(par_y)))
                ax[i].text(year[0],np.max(par_y),"y="+str(round(beta1,2))+'x'+str(round(beta0,2))+'    '+'$\it{R}$$^2$='+str(round(R2,2))+'\n'+strp+'    '+'SD='+str(round(sigma,2)),fontsize=12) 
                ax[i].set(ylabel = parameters_list[i])
            plt.rcParams['font.size']=12
            plt.rcParams['font.family']='arial'
            plt.rcParams['xtick.labelsize']=12
            plt.rcParams['ytick.labelsize']=12
            plt.rcParams['xtick.major.pad']=8
            plt.rcParams['ytick.major.pad']=8
            plt.tight_layout()    
            plt.savefig(out_path+'EcoParameter_Basin_Year.tif',bbox_inches='tight',dpi=300)
def Cent_hru_space_data(folder_path,begin_year,end_year,parameters_list,out_path,flag):
    CENT_hru_df,hru_num,sub_num = read_DayCent_output(folder_path)
    CENT_hru_year = CENT_hru_df[(CENT_hru_df['Y']<=end_year)&(CENT_hru_df['Y']>=begin_year)]
    Pars_hru_mean_slope = pd.DataFrame()
    Pars_hru_mean_slope["HRU_ID"] = np.arange(1,hru_num+1,1)
    for par in parameters_list:
        par_year_hru = pd.pivot_table(CENT_hru_year,index=['iHRU'],columns='Y',values= par ,aggfunc=[np.mean])
        par_name = par.split('/')[0]
        par_year_hru[par_name+"_ymean"] = par_year_hru.iloc[:,:].apply(lambda x: x.mean(),axis=1)
        par_year_hru_trend = []
        for hru in range(hru_num):
            beta1,beta0,p,R2,rmse,sigma = linear_fit(range(begin_year,end_year+1,1),par_year_hru.iloc[hru,:-1].values)
            par_year_hru_trend.append(beta1)
        par_year_hru[par_name+"_yslope"] = par_year_hru_trend
        #增加HRU_ID一列
        index_num = [int(i) for i in par_year_hru.index]
        par_year_hru['HRU_ID'] = index_num
        #colnames重置
        year_list = np.arange(begin_year, end_year+1 , 1).tolist()
        par_col_name = [par_name+"_"+str(i) for i in year_list]
        par_col_name.extend([ par_name+"_ymean",par_name+"_yslope","HRU_ID"])
        par_year_hru.columns = par_col_name
        par_year_hru = par_year_hru.sort_values(by='HRU_ID')
        par_hru = par_year_hru[[par_name+"_ymean",par_name+"_yslope","HRU_ID"]]
        Pars_hru_mean_slope = Pars_hru_mean_slope.merge(par_hru,on = 'HRU_ID', how = 'left')
    Pars_hru_mean_slope.to_csv(out_path+'EcoParameter_Hru_mean_slope.csv',sep=',',index=False,header=True)
    if flag ==1:
        data = Pars_hru_mean_slope
        data_geod = gp.GeoDataFrame(data)
        hru_shp=folder_path+"/Watershed/Shapes/hru1.shp"
        hru_geom  = gp.GeoDataFrame.from_file(hru_shp, encoding = 'gb18030')
        hru_data = hru_geom.merge(data_geod, on = 'HRU_ID', how = 'left')
        subplot_row = len(parameters_list)
        fig,ax=plt.subplots(nrows=subplot_row, ncols=2,figsize=(6*2,4*subplot_row),sharex=False,sharey=False)
        print('plotting hru space distribution...')
        if subplot_row == 1:
            par = parameters_list[0].split('/')[0]
            bins1,nbin1 = d_bins(data[par+"_ymean"])
            bins1 = np.round(bins1,0)
            cmap1 = cm.get_cmap('Spectral', nbin1)
            norm1 = mcolors.BoundaryNorm(bins1, nbin1)
            hru_data.plot(par+"_ymean",ax = ax[0], k=12,norm  = norm1,cmap = cmap1)
            ax[0].axis('off')
            im1 = cm.ScalarMappable(norm=norm1, cmap= cmap1)
            cbar1 = fig.colorbar(
                im1, ax=ax[0], orientation='horizontal',
                shrink=0.5,pad = 0,
                label= parameters_list[0]
                )

            bins2,nbin2 = d_bins(data[par+"_yslope"])
            bins2 = np.round(bins2,1)
            cmap2 = cm.get_cmap('PiYG', nbin2)
            norm2 = mcolors.BoundaryNorm(bins2, nbin2)
            hru_data.plot(par+"_yslope",ax = ax[1], k=12,norm  = norm2,cmap = cmap2)
            ax[1].axis('off')
            im2 = cm.ScalarMappable(norm=norm2, cmap= cmap2)
            cbar2 = fig.colorbar(
                im2, ax=ax[1], orientation='horizontal',
                shrink=0.5,pad = 0,
                label= par+" trend"
                )
            plt.rcParams['font.size']=12
            plt.rcParams['font.family']='arial'
            plt.subplots_adjust(wspace=-0.15,hspace=0)
            plt.savefig(out_path+'EcoParameter_Hru_distribution.tif',bbox_inches='tight',dpi=300)
        else:
            for i in range(subplot_row):
                par = parameters_list[i].split('/')[0]
                bins1,nbin1 = d_bins(data[par+"_ymean"])
                bins1 = np.round(bins1,0)
                cmap1 = cm.get_cmap('Spectral', nbin1)
                norm1 = mcolors.BoundaryNorm(bins1, nbin1)
                hru_data.plot(par+"_ymean",ax = ax[i][0], k=12,norm  = norm1,cmap = cmap1)
                ax[i][0].axis('off')
                im1 = cm.ScalarMappable(norm=norm1, cmap= cmap1)
                cbar1 = fig.colorbar(
                    im1, ax=ax[i][0], orientation='horizontal',
                    shrink=0.5,pad = 0,
                    label= parameters_list[i]
                    )

                bins2,nbin2 = d_bins(data[par+"_yslope"].round(2))
                bins2 = np.round(bins2,1)
                cmap2 = cm.get_cmap('PiYG', nbin2)
                norm2 = mcolors.BoundaryNorm(bins2, nbin2)
                hru_data.plot(par+"_yslope",ax = ax[i][1], k=12,norm  = norm2,cmap = cmap2)
                ax[i][1].axis('off')
                im2 = cm.ScalarMappable(norm=norm2, cmap= cmap2)
                cbar2 = fig.colorbar(
                    im2, ax=ax[i][1], orientation='horizontal',
                    shrink=0.5,pad = 0,
                    label= par+" trend"
                    )
            plt.rcParams['font.size']=12
            plt.rcParams['font.family']='arial'
            plt.subplots_adjust(wspace=-0.15,hspace=0.1)
            plt.savefig(out_path+'EcoParameter_Hru_distribution.tif',bbox_inches='tight',dpi=300)
#SUB尺度上的分析（空间分布和空间趋势）
def Cent_sub_space_data(folder_path,begin_year,end_year,parameters_list,out_path,flag):
    CENT_hru_df,hru_num,sub_num = read_DayCent_output(folder_path)
    CENT_sub_year = CENT_hru_df[(CENT_hru_df['Y']<=end_year)&(CENT_hru_df['Y']>=begin_year)]
    Pars_sub_mean_slope = pd.DataFrame()
    Pars_sub_mean_slope["Subbasin"] = np.arange(1,sub_num+1,1)
    for par in parameters_list:
        par_year_sub = pd.pivot_table(CENT_sub_year,index=['iSUB'],columns='Y',values= par ,aggfunc=[np.mean])
        par_name = par.split(' ')[0]
        par_year_sub[par_name+"_ymean"] = par_year_sub.iloc[:,:].apply(lambda x: x.mean(),axis=1)
        par_year_sub_trend = []
        for sub in range(sub_num):
            beta1,beta0,p,R2,rmse,sigma = linear_fit(range(begin_year,end_year+1,1),par_year_sub.iloc[sub,:-1].values)
            par_year_sub_trend.append(beta1)
        par_year_sub[par_name+"_yslope"] = par_year_sub_trend
        #增加Subbasin一列
        index_num = [int(i) for i in par_year_sub.index]
        par_year_sub['Subbasin'] = index_num
        #colnames重置
        year_list = np.arange(begin_year, end_year+1 , 1).tolist()
        par_col_name = [par_name+"_"+str(i) for i in year_list]
        par_col_name.extend([ par_name+"_ymean",par_name+"_yslope","Subbasin"])
        par_year_sub.columns = par_col_name
        par_year_sub = par_year_sub.sort_values(by='Subbasin')
        par_sub = par_year_sub[[par_name+"_ymean",par_name+"_yslope","Subbasin"]]
        Pars_sub_mean_slope = Pars_sub_mean_slope.merge(par_sub,on = 'Subbasin', how = 'left')
    Pars_sub_mean_slope.to_csv(out_path+'EcoParameter_Sub_mean_slope.csv',sep=',',index=False,header=True)
    if flag ==1:
        data = Pars_sub_mean_slope
        data_geod = gp.GeoDataFrame(data)
        sub_shp=folder_path+"/Watershed/Shapes/subs1.shp"
        sub_geom  = gp.GeoDataFrame.from_file(sub_shp, encoding = 'gb18030')
        sub_data = sub_geom.merge(data_geod, on = 'Subbasin', how = 'left')
        subplot_row = len(parameters_list)
        fig,ax=plt.subplots(nrows=subplot_row, ncols=2,figsize=(6*2,4*subplot_row),sharex=False,sharey=False)
        print('plotting sub space distribution...')
        if subplot_row==1:
            par = parameters_list[0].split(' ')[0]
            bins1,nbin1 = d_bins(data[par+"_ymean"])
            bins1 = np.round(bins1,0)
            cmap1 = cm.get_cmap('Spectral', nbin1)
            norm1 = mcolors.BoundaryNorm(bins1, nbin1)
            sub_data.plot(par+"_ymean",ax = ax[0], k=12,norm  = norm1,cmap = cmap1)
            ax[0].axis('off')
            im1 = cm.ScalarMappable(norm=norm1, cmap= cmap1)
            cbar1 = fig.colorbar(
                im1, ax=ax[0], orientation='horizontal',
                shrink=0.5,pad = 0,
                label= parameters_list[0]
                )

            bins2,nbin2 = d_bins(data[par+"_yslope"])
            bins2 = np.round(bins2,1)
            cmap2 = cm.get_cmap('PiYG', nbin2)
            norm2 = mcolors.BoundaryNorm(bins2, nbin2)
            sub_data.plot(par+"_yslope",ax = ax[1], k=12,norm  = norm2,cmap = cmap2)
            ax[1].axis('off')
            im2 = cm.ScalarMappable(norm=norm2, cmap= cmap2)
            cbar2 = fig.colorbar(
                im2, ax=ax[1], orientation='horizontal',
                shrink=0.5,pad = 0,
                label= par+" trend"
                )
            plt.rcParams['font.size']=12
            plt.rcParams['font.family']='arial'
            plt.subplots_adjust(wspace=-0.15,hspace=0)
            plt.savefig(out_path+'EcoParameter_Sub_distribution.tif',bbox_inches='tight',dpi=300)
        else: 
            for i in range(subplot_row):
                par = parameters_list[i].split(' ')[0]
                bins1,nbin1 = d_bins(data[par+"_ymean"])
                bins1 = np.round(bins1,0)
                cmap1 = cm.get_cmap('Spectral', nbin1)
                norm1 = mcolors.BoundaryNorm(bins1, nbin1)
                sub_data.plot(par+"_ymean",ax = ax[i][0], k=12,norm  = norm1,cmap = cmap1)
                ax[i][0].axis('off')
                im1 = cm.ScalarMappable(norm=norm1, cmap= cmap1)
                cbar1 = fig.colorbar(
                    im1, ax=ax[i][0], orientation='horizontal',
                    shrink=0.5,pad = 0,
                    label= parameters_list[i]
                    )

                bins2,nbin2 = d_bins(data[par+"_yslope"].round(2))
                bins2 = np.round(bins2,1)
                cmap2 = cm.get_cmap('PiYG', nbin2)
                norm2 = mcolors.BoundaryNorm(bins2, nbin2)
                sub_data.plot(par+"_yslope",ax = ax[i][1], k=12,norm  = norm2,cmap = cmap2)
                ax[i][1].axis('off')
                im2 = cm.ScalarMappable(norm=norm2, cmap= cmap2)
                cbar2 = fig.colorbar(
                    im2, ax=ax[i][1], orientation='horizontal',
                    shrink=0.5,pad = 0,
                    label= par+" trend"
                    )
            plt.rcParams['font.size']=12
            plt.rcParams['font.family']='arial'
            plt.subplots_adjust(wspace=-0.15,hspace=0.1)
            plt.savefig(out_path+'EcoParameter_Sub_distribution.tif',bbox_inches='tight',dpi=300)
def Cent_lulc_year(folder_path,begin_year,end_year,parameters_list,out_path):
    CENT_hru_df,hru_num,sub_num = read_DayCent_output(folder_path)
    CENT_sub_year = CENT_hru_df[(CENT_hru_df['Y']<=end_year)&(CENT_hru_df['Y']>=begin_year)]
    Pars_lulc_ny_mean = pd.DataFrame()
    for par in parameters_list:
        par_lulc_y = pd.pivot_table(CENT_sub_year ,index=['Y'],columns='LC',values= par ,aggfunc=[np.mean])
        par_lulc_y.columns = [i[1] for i in par_lulc_y.columns]
        par_name = par.split('/')[0]
        par_lulc_y.to_csv(out_path+par_name+'_lulc_year.csv',sep=',',index=True,header=True)
        Pars_lulc_ny_mean[par_name] = np.mean(par_lulc_y)
    Pars_lulc_ny_mean.to_csv(out_path+'EcosPars_lulc_ny_mean.csv',sep=',',index=True,header=True) 
    Pars_lulc_ny_mean[:-1].plot(use_index=True, kind='bar',subplots=False,figsize = (4,3))
    plt.rcParams['font.size']=12
    plt.rcParams['font.family']='arial'
    plt.rcParams['xtick.labelsize']=14
    plt.rcParams['ytick.labelsize']=14
    plt.rcParams['xtick.major.pad']=8
    plt.rcParams['ytick.major.pad']=8
    plt.legend(loc ='upper left',edgecolor = 'none',facecolor = 'none')
    plt.savefig(out_path+'EcoPars_lulc_ny_mean.tif',bbox_inches='tight',dpi=300) 


if __name__ == '__main__':
    folder_path = r"D:/SWAT_Daycent_software_test/SWAT_DayCent_Pro"
    begin_year = 2000
    end_year = 2019  
    out_path = "D:/SWAT_Daycent_software_test/SWAT_DayCent_Pro/output_result/"
    flag = 1
    time = ["year","month","season"]
    #不同的函数
    parameters_list = ["PCP/mm","ET/mm","SW_END/mm"]
    SWAT_output_basin(folder_path,begin_year,end_year,parameters_list,out_path,flag,time)#1
    
    SWAT_lulc_year(folder_path,begin_year,end_year,parameters_list,out_path) #5
    SWAT_hru_space_data(folder_path,begin_year,end_year,parameters_list,out_path,flag)#4

    parameters_list = ['FLOW_OUT/cms','SED_OUT/tons']
    SWAT_rch_space_data(folder_path,begin_year,end_year,parameters_list,out_path,flag)#3

    parameters_list = ['SYLD/t/ha','ORGN/kg/ha']
    SWAT_sub_space_data(folder_path,begin_year,end_year,parameters_list,out_path,flag)#2

    parameters_list = ["cproda", "aglivc" ]
    Cent_output_basin(folder_path,begin_year,end_year,parameters_list,out_path,flag)#b
    Cent_hru_space_data(folder_path,begin_year,end_year,parameters_list,out_path,flag)#h
    Cent_sub_space_data(folder_path,begin_year,end_year,parameters_list,out_path,flag)#s
    Cent_lulc_year(folder_path,begin_year,end_year,parameters_list,out_path)#l
