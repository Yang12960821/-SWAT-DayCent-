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
from osgeo import ogr,gdal,osr
from mpl_toolkits.basemap import Basemap
import xarray as xr
from pyproj import Proj
import matplotlib
import matplotlib.colors as mcolors
import pygeoprocessing
import math
import natcap.invest.sdr.sdr
import natcap.invest.carbon
import natcap.invest.utils


def read_rasterfile(input_rasterfile):
    dataset=gdal.Open(input_rasterfile)
    
    im_width=dataset.RasterXSize
    im_height=dataset.RasterYSize
    im_bands=dataset.RasterCount
    
    im_geotrans=dataset.GetGeoTransform()
    im_proj=dataset.GetProjection()
    
    im_data=dataset.ReadAsArray(0,0,im_width,im_height)
    NoDataValue=dataset.GetRasterBand(1).GetNoDataValue()
    return [im_data,im_width,im_height,im_bands,im_geotrans,im_proj,NoDataValue]

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

# 分区统计相关计算
def boundingBoxToOffsets(bbox, geot):
    col1 = int(round((bbox[0] - geot[0]) / geot[1]))
    col2 = int(round((bbox[1] - geot[0]) / geot[1]))
    row1 = int(round((bbox[3] - geot[3]) / geot[5]))
    row2 = int(round((bbox[2] - geot[3]) / geot[5]))
    return [row1, row2, col1, col2]

def geotFromOffsets(row_offset, col_offset, geot):
    new_geot = [
    geot[0] + (col_offset * geot[1]),
    geot[1],
    0.0,
    geot[3] + (row_offset * geot[5]),
    0.0,
    geot[5]
    ]
    return new_geot

def setFeatureStats(fid, min, max, mean, median, sd, sum, count, names=["min", "max", "mean", "median", "sd", "sum", "count", "id"]):
    featstats = {
    names[0]: min,
    names[1]: max,
    names[2]: mean,
    names[3]: median,
    names[4]: sd,
    names[5]: sum,
    names[6]: count,
    names[7]: fid,
    }
    return featstats

# def zonal(fn_raster, fn_zones, fn_csv):
def zonal(fn_raster, fn_zones):
    mem_driver = ogr.GetDriverByName("Memory")
    mem_driver_gdal = gdal.GetDriverByName("MEM")
    shp_name = "deg"

#     fn_raster = r"D:\Wangfan_File\QNNR\QLM_SUB\deg_sum_c1.tif"
#     fn_zones = r"D:\Wangfan_File\QNNR\QLM_SUB\Export_Output.shp"

    r_ds = gdal.Open(fn_raster)
    p_ds = ogr.Open(fn_zones)

    lyr = p_ds.GetLayer()
    geot = r_ds.GetGeoTransform()
    nodata = r_ds.GetRasterBand(1).GetNoDataValue()

    zstats = []

    p_feat = lyr.GetNextFeature()
    niter = 0

    while p_feat:
        if p_feat.GetGeometryRef() is not None:
            if os.path.exists(shp_name):
                mem_driver.DeleteDataSource(shp_name)
            tp_ds = mem_driver.CreateDataSource(shp_name)
            tp_lyr = tp_ds.CreateLayer('polygons', None, ogr.wkbPolygon)
            tp_lyr.CreateFeature(p_feat.Clone())
            offsets = boundingBoxToOffsets(p_feat.GetGeometryRef().GetEnvelope(),\
            geot)
            new_geot = geotFromOffsets(offsets[0], offsets[2], geot)

            tr_ds = mem_driver_gdal.Create(\
            "", \
            offsets[3] - offsets[2], \
            offsets[1] - offsets[0], \
            1, \
            gdal.GDT_Byte)

            tr_ds.SetGeoTransform(new_geot)
            gdal.RasterizeLayer(tr_ds, [1], tp_lyr, burn_values=[1])
            tr_array = tr_ds.ReadAsArray()

            r_array = r_ds.GetRasterBand(1).ReadAsArray(\
            offsets[2],\
            offsets[0],\
            offsets[3] - offsets[2],\
            offsets[1] - offsets[0])
#             print(r_array)
        #删除小于0的值
#             r_array[r_array==nodata] = np.nan
            r_array[r_array<0.0] = np.nan
            
#             id = p_feat.GetFID()
            id = p_feat.GetField('HRU_ID')

            if r_array is not None:
                maskarray = np.ma.MaskedArray(\
                r_array,\
                mask=np.logical_or(r_array==nodata, np.logical_not(tr_array)))
                 
                if maskarray is not None:
                    zstats.append(setFeatureStats(\
                id,\
                np.nanmin(maskarray),\
                np.nanmax(maskarray),\
                np.nanmean(maskarray),\
                np.ma.median(maskarray),\
                maskarray.std(),\
                np.nansum(maskarray),\
                maskarray.count()))
                else:
                    zstats.append(setFeatureStats(\
                    id,\
                    nodata,\
                    nodata,\
                    nodata,\
                    nodata,\
                    nodata,\
                    nodata,\
                    nodata))
            else:
                zstats.append(setFeatureStats(\
                    id,\
                    nodata,\
                    nodata,\
                    nodata,\
                    nodata,\
                    nodata,\
                    nodata,\
                    nodata))

            tp_ds = None
            tp_lyr = None
            tr_ds = None

            p_feat = lyr.GetNextFeature()
            
    col_names = zstats[0].keys()
    zstats = DataFrame(zstats)
    zstats.sort_values(by='id',inplace=True)
    zstats["mean"]
    return zstats["mean"]

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

#水源涵养模块
#M1:P-ET-SURF
def WR1_output(folder_path,begin_year,end_year,out_path,flag):
    output_hru_df,hru_num = read_SWAT_output_hru(folder_path)
    basin_area = np.sum(output_hru_df["AREAkm2"][:hru_num])    
    output_hru_year = output_hru_df[(output_hru_df['MON']<=end_year)&(output_hru_df['MON']>=begin_year)]
    output_hru_year["AREAkm2"] = output_hru_year["AREAkm2"]/basin_area
    output_hru_year["WR/mm"] = output_hru_year["PCP/mm"]-output_hru_year["ET/mm"]-output_hru_year["SURQ_GEN/mm"]
    year_seq = np.arange(begin_year,end_year+1 , 1)
    WR1_y = pd.DataFrame()
    WR1_y['Year'] = year_seq
    par = "WR/mm"
    unit = par.split('/')[1]
    
    output_hru_year[par] = output_hru_year["AREAkm2"]*output_hru_year[par]
    par_y = pd.pivot_table(output_hru_year,index=['MON'],values = par, aggfunc="sum")
    WR1_y[par] = par_y[par].tolist()
    WR1_y.to_csv(out_path+'/WR1_Basin_Year.csv',sep=',',index=False,header=True)
    
    if flag==1:
        fig,ax=plt.subplots(figsize=(4,3),sharex=False, sharey=False)
        print('plotting WR1 basin year trend...')
        year = WR1_y['Year']
        par_y = WR1_y[par]
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
        ax.set(ylabel = par)
        plt.rcParams['font.size']=12
        plt.rcParams['font.family']='arial'
        plt.rcParams['xtick.labelsize']=12
        plt.rcParams['ytick.labelsize']=12
        plt.rcParams['xtick.major.pad']=8
        plt.rcParams['ytick.major.pad']=8
        plt.tight_layout()
        plt.savefig(out_path+'/WR1_Basin_Year.tif',bbox_inches='tight',dpi=300)
        
    #SUB尺度计算
    output_sub_df,sub_num = read_SWAT_output_sub(folder_path)
    output_sub_year = output_sub_df[(output_sub_df['MON']<=end_year)&(output_sub_df['MON']>=begin_year)]
    output_sub_year["WR/mm"] = output_sub_year["PCP/mm"]-output_sub_year["ET/mm"]-output_sub_year["SURQ/mm"]
    WR1_sub_mean_slope = pd.DataFrame()
    WR1_sub_mean_slope["Subbasin"] = np.arange(1,sub_num+1,1)
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
#     par_year_sub.to_csv(out_path+'NPP_Sub_ny.csv',sep=',',index=False,header=True)    
    par_sub = par_year_sub[[par_name+"_ymean",par_name+"_yslope","Subbasin"]]
    WR1_sub_mean_slope = WR1_sub_mean_slope.merge(par_sub,on = 'Subbasin', how = 'left')
    WR1_sub_mean_slope.to_csv(out_path+'/WR1_Sub_mean_slope.csv',sep=',',index=False,header=True)    
    
    if flag ==1:
        data = WR1_sub_mean_slope
        data_geod = gp.GeoDataFrame(data)
        sub_shp=folder_path+"/Watershed/Shapes/subs1.shp"
        sub_geom  = gp.GeoDataFrame.from_file(sub_shp, encoding = 'gb18030')
        sub_data = sub_geom.merge(data_geod, on = 'Subbasin', how = 'left')
        fig,ax=plt.subplots(nrows=1, ncols=2,figsize=(6*2,4),sharex=False,sharey=False)
        print('plotting sub space distribution...')
        par0 = par.split('/')[0]
        bins1,nbin1 = d_bins(data[par_name+"_ymean"])
        bins1 = np.round(bins1,0)
        cmap1 = cm.get_cmap('Spectral', nbin1)
        norm1 = mcolors.BoundaryNorm(bins1, nbin1)
        sub_data.plot(par0+"_ymean",ax = ax[0], k=12,norm  = norm1,cmap = cmap1)
        ax[0].axis('off')
        im1 = cm.ScalarMappable(norm=norm1, cmap= cmap1)
        cbar1 = fig.colorbar(
            im1, ax=ax[0], orientation='horizontal',
            shrink=0.5,pad = 0,
            label= par
            )
        bins2,nbin2 = d_bins(data[par_name+"_yslope"])
        bins2 = np.round(bins2,1)
        cmap2 = cm.get_cmap('PiYG', nbin2)
        norm2 = mcolors.BoundaryNorm(bins2, nbin2)
        sub_data.plot(par0+"_yslope",ax = ax[1], k=12,norm  = norm2,cmap = cmap2)
        ax[1].axis('off')
        im2 = cm.ScalarMappable(norm=norm2, cmap= cmap2)
        cbar2 = fig.colorbar(
            im2, ax=ax[1], orientation='horizontal',
            shrink=0.5,pad = 0,
            label= par_name+" trend "+unit+"/"+"y"
            )
        plt.rcParams['font.size']=12
        plt.rcParams['font.family']='arial'
        plt.subplots_adjust(wspace=-0.15,hspace=0)
        plt.savefig(out_path+'/WR1_Sub_distribution.tif',bbox_inches='tight',dpi=300)
    
    #HRU尺度计算
    output_hru_year = output_hru_df[(output_hru_df['MON']<=end_year)&(output_hru_df['MON']>=begin_year)]
    output_hru_year["WR/mm"] = output_hru_year["PCP/mm"]-output_hru_year["ET/mm"]-output_hru_year["SURQ_GEN/mm"]
    WR1_hru_mean_slope = pd.DataFrame()
    WR1_hru_mean_slope["HRU_ID"] = np.arange(1,hru_num+1,1)
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
#     par_year_hru.to_csv(out_path+'SYLD_Hru_ny.csv',sep=',',index=False,header=True)
    par_hru = par_year_hru[[par_name+"_ymean",par_name+"_yslope","HRU_ID"]]
    WR1_hru_mean_slope = WR1_hru_mean_slope.merge(par_hru,on = 'HRU_ID', how = 'left')
    WR1_hru_mean_slope.to_csv(out_path+'/WR1_Hru_mean_slope.csv',sep=',',index=False,header=True)
    
    if flag==1:
        data = WR1_hru_mean_slope
        data_geod = gp.GeoDataFrame(data)
        hru_shp=folder_path+"/Watershed/Shapes/hru1.shp"
        hru_geom  = gp.GeoDataFrame.from_file(hru_shp, encoding = 'gb18030')
        hru_data = hru_geom.merge(data_geod, on = 'HRU_ID', how = 'left')
        fig,ax=plt.subplots(nrows=1, ncols=2,figsize=(6*2,4),sharex=False,sharey=False)
        print('plotting hru space distribution...')
        par0 = par.split('/')[0]
        bins1,nbin1 = d_bins(data[par_name +"_ymean"])
        bins1 = np.round(bins1,1)
        cmap1 = cm.get_cmap('Spectral', nbin1)
        norm1 = mcolors.BoundaryNorm(bins1, nbin1)
        hru_data.plot(par0+"_ymean",ax = ax[0], k=12,norm  = norm1,cmap = cmap1)
        ax[0].axis('off')
        im1 = cm.ScalarMappable(norm=norm1, cmap= cmap1)
        cbar1 = fig.colorbar(
            im1, ax=ax[0], orientation='horizontal',
            shrink=0.5,pad = 0,
            label= par
            )

        bins2,nbin2 = d_bins(data[par_name+"_yslope"])
        bins2 = np.round(bins2,2)
        cmap2 = cm.get_cmap('PiYG', nbin2)
        norm2 = mcolors.BoundaryNorm(bins2, nbin2)
        hru_data.plot(par0+"_yslope",ax = ax[1], k=12,norm  = norm2,cmap = cmap2)
        ax[1].axis('off')
        im2 = cm.ScalarMappable(norm=norm2, cmap= cmap2)
        cbar2 = fig.colorbar(
            im2, ax=ax[1], orientation='horizontal',
            shrink=0.5,pad = 0,
            label= par_name+" trend "+unit+"/"+"y"
            )
        plt.rcParams['font.size']=12
        plt.rcParams['font.family']='arial'
        plt.subplots_adjust(wspace=-0.15,hspace=0)
        plt.savefig(out_path+'/WR1_Hru_distribution.tif',bbox_inches='tight',dpi=300)



def twi_function(dem_dir,watershed_dir,output_dir):
    pixel_size = read_rasterfile(dem_dir)[4][1]
    pixel_size2 = pixel_size**2
    pygeoprocessing.calculate_slope((dem_dir,1),output_dir+"dem_slope.tif")
    slope_data=read_rasterfile(output_dir+"dem_slope.tif")
    slope_array = np.where(slope_data[0] == slope_data[-1], np.nan, slope_data[0])
    slope_array = np.where(slope_array ==0, 0.001, slope_array)

    flow_accumulation_data=read_rasterfile(watershed_dir+"Grid/flowacc")
    flow_accumulation_array = np.where(flow_accumulation_data[0] == flow_accumulation_data[-1], np.nan, slope_data[0])

    direction_data=read_rasterfile(watershed_dir+"Grid/flowdir")
    flow_direction = np.where(direction_data[0] == direction_data[-1],np.nan ,direction_data[0])
    flow_width1 = np.where(flow_direction ==1&4&16&64, pixel_size ,flow_direction)
    flow_width2 = np.where(flow_width1  ==2&8&32&128, pixel_size*np.nan ,flow_width1 )
    slope_array= np.tan(slope_array)
    twi = np.log(((flow_accumulation_array+1)*pixel_size2)/(flow_width2*slope_array))
    twi[np.isinf(twi)]=0
    out_tif_name = output_dir+"/TI_result.tif"
    driver = gdal.GetDriverByName("GTiff")
    out_tif = driver.Create(out_tif_name, read_rasterfile(dem_dir)[1], read_rasterfile(dem_dir)[2], 1, gdal.GDT_Float32)
    geotransform = read_rasterfile(dem_dir)[4]
    out_tif.SetGeoTransform(geotransform)        
    srs = osr.SpatialReference()
    proj_type = read_rasterfile(dem_dir)[5]
    out_tif.SetProjection(proj_type)  
    # 数据写出        
    out_tif.GetRasterBand(1).WriteArray(twi)  
    out_tif.FlushCache()  # 将数据写入硬盘
    out_tif = None  # 注意必须关闭tif文件
    
    fn_zones = watershed_dir+"Shapes/hru1.shp"
    fn_raster = out_tif_name
    TI = zonal(fn_raster, fn_zones)
    TI_index = np.where(0.3*TI>=1,1.0,0.3*TI)
    return TI_index

def WR_Index(dem_dir,watershed_dir,Ksat_dir,Vel_dir,folder_Path,output_dir):
    TI_index = twi_function(dem_dir,watershed_dir,output_dir)

    Ksat_df = pd.read_csv(Ksat_dir)
    Ksat_df['min_Ksat_1']= Ksat_df['SOL_K']*24/300
    for i in range(Ksat_df.shape[0]):
            Ksat_df['min_Ksat_1'][i]=min(Ksat_df['min_Ksat_1'][i],1.0)

    Veol_df = pd.read_csv(Vel_dir)
    Veol_df['min_Vel_1'] = 249/Veol_df['Vel_coef']
    for i in range(Veol_df.shape[0]):
           Veol_df['min_Vel_1'][i]=min(Veol_df['min_Vel_1'][i],1.0)
    Ksat_df.columns = ["VALUE","Soil","SOL_K","min_Ksat_1"]
    Veol_df.columns = ["VALUE","LULC","Vel_coef","min_Vel_1"]

    input_std = folder_Path+"/TxtInOut/input.std"
    input_std = pd.read_table(input_std)
    string = "         HRU CN Input Summary Table:"
    input_std_list = input_std.iloc[:,0].tolist()
    num = input_std_list.index(string)
    hru_num = len(TI_index)
    input_table = input_std[num+1:num+hru_num+2]
    soil_lulc_attribute = input_table["1"].str.split(pat="\s+",expand=True).iloc[:,:6]
    soil_lulc_attribute.columns = soil_lulc_attribute.iloc[0,:].tolist()
    soil_lulc_attribute = soil_lulc_attribute[1:]
    m  = pd.merge(soil_lulc_attribute, Ksat_df,on = "Soil")
    m = pd.merge(m,Veol_df ,on = "LULC")
    m["HRU"] = pd.to_numeric(m["HRU"])
    m.sort_values(by = "HRU")

    Ksat_Index = np.array(m['min_Ksat_1'])
    Vel_Index = np.array(m['min_Vel_1'])
    WR_Index = TI_index*Ksat_Index*Vel_Index 
    WR_Index  = DataFrame(WR_Index)

    Ksat_Index = np.array(m['min_Ksat_1'])
    Vel_Index = np.array(m['min_Vel_1'])
    WR_Index = TI_index*Ksat_Index*Vel_Index 
    WR_Index = DataFrame(WR_Index)
    return WR_Index

def WYLD_output(folder_path,begin_year,end_year,output_dir,flag):
    output_hru_df,hru_num = read_SWAT_output_hru(folder_path)
    basin_area = np.sum(output_hru_df["AREAkm2"][:hru_num])    
    output_hru_year = output_hru_df[(output_hru_df['MON']<=end_year)&(output_hru_df['MON']>=begin_year)]
    output_hru_year["AREAkm2"] = output_hru_year["AREAkm2"]/basin_area
    year_seq = np.arange(begin_year,end_year+1 , 1)
    WYLD_y = pd.DataFrame()
    WYLD_y['Year'] = year_seq
    par = "WYLD/mm"
    unit = par.split('/')[1]
    
    output_hru_year[par] = output_hru_year["AREAkm2"]*output_hru_year[par]
    par_y = pd.pivot_table(output_hru_year,index=['MON'],values = par, aggfunc="sum")
    WYLD_y[par] = par_y[par].tolist()      
    WYLD_y.to_csv(output_dir+'WYLD_Year.csv',sep=',',index=False,header=True)
    
    #HRU尺度计算
    output_hru_year = output_hru_df[(output_hru_df['MON']<=end_year)&(output_hru_df['MON']>=begin_year)]
    WYLD_hru_mean_slope = pd.DataFrame()
    WYLD_hru_mean_slope["HRU_ID"] = np.arange(1,hru_num+1,1)
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
    par_year_hru.to_csv(output_dir+'WYLD_Hru_ny.csv',sep=',',index=False,header=True)
    par_hru = par_year_hru[[par_name+"_ymean",par_name+"_yslope","HRU_ID"]]
    WYLD_hru_mean_slope = WYLD_hru_mean_slope.merge(par_hru,on = 'HRU_ID', how = 'left')
    return par_year_hru

def WR2_output(dem_dir,watershed_dir,Ksat_dir,Vel_dir,folder_path,begin_year,end_year,output_dir,flag):
    wr_index = WR_Index(dem_dir,watershed_dir,Ksat_dir,Vel_dir,folder_path,output_dir)
    WYLD = WYLD_output(folder_path,begin_year,end_year,output_dir,flag)
    
    year_list = np.arange(begin_year, end_year+1 , 1).tolist()
    wr_col_name = ["WR_"+str(i) for i in year_list]
    wr_col_name.extend([ "wr_ymean","wr_yslope","HRU_ID"])
    WR2 = WYLD
    WR2.columns = wr_col_name
    for i in range(WR2.shape[0]):
        for j in range(WR2.shape[1]-3):
            WR2.iloc[i,j] = WYLD.iloc[i,j]*wr_index.iloc[i,0]
    WR2["wr_ymean"] = WR2.apply(lambda x: x.mean(),axis=1)   
    WR2 = WR2.fillna(1)
    wr_year_hru_trend = []
    
    for hru in range(WR2.shape[0]):
        beta1,beta0,p,R2,rmse,sigma = linear_fit(range(begin_year,end_year+1,1),WR2.iloc[hru,:-3].values)
        wr_year_hru_trend.append(beta1)
    WR2["wr_yslope"] = wr_year_hru_trend
    WR2_Year = WR2.mean()
    WR2_Year.to_csv(output_dir+'WR2_Basin_Year.csv',sep=',',index=True,header=True)
    WR2.to_csv(output_dir+'WR2_hru_space.csv',sep=',',index=True,header=True)
    
    
    if flag==1:
        data = WR2
        data_geod = gp.GeoDataFrame(data)
        hru_shp=folder_path+"/Watershed/Shapes/hru1.shp"
        hru_geom  = gp.GeoDataFrame.from_file(hru_shp, encoding = 'gb18030')
        hru_data = hru_geom.merge(data_geod, on = 'HRU_ID', how = 'left')
        fig,ax=plt.subplots(nrows=1, ncols=2,figsize=(6*2,4),sharex=False,sharey=False)

        bins1,nbin1 = d_bins(data["wr_ymean"])
        bins1 = np.round(bins1,0)
        cmap1 = cm.get_cmap('Spectral', nbin1)
        norm1 = mcolors.BoundaryNorm(bins1, nbin1)
        hru_data.plot("wr_ymean",ax = ax[0], k=12,norm  = norm1,cmap = cmap1)
        ax[0].axis('off')
        im1 = cm.ScalarMappable(norm=norm1, cmap= cmap1)
        cbar1 = fig.colorbar(
            im1, ax=ax[0], orientation='horizontal',
            shrink=0.5,pad = 0,
            label= "WR/mm"
            )

        bins2,nbin2 = d_bins(data["wr_yslope"])
        bins2 = np.round(bins2,1)
        cmap2 = cm.get_cmap('PiYG', nbin2)
        norm2 = mcolors.BoundaryNorm(bins2, nbin2)
        hru_data.plot("wr_yslope",ax = ax[1], k=12,norm  = norm2,cmap = cmap2)
        ax[1].axis('off')
        im2 = cm.ScalarMappable(norm=norm2, cmap= cmap2)
        cbar2 = fig.colorbar(
            im2, ax=ax[1], orientation='horizontal',
            shrink=0.5,pad = 0,
            label= "WR trend/mm/y"
            )
        plt.rcParams['font.size']=12
        plt.rcParams['font.family']='arial'
        plt.subplots_adjust(wspace=-0.15,hspace=0)
        plt.savefig(output_dir+'WR2_Hru_distribution.tif',bbox_inches='tight',dpi=300)
        
        
#土壤侵蚀模块---------------------------------------------------------------------------------------------------------
#M1:
def SWAT_output_syld(folder_path,begin_year,end_year,out_path,flag):
    output_hru_df,hru_num = read_SWAT_output_hru(folder_path)
    basin_area = np.sum(output_hru_df["AREAkm2"][:hru_num])    
    output_hru_year = output_hru_df[(output_hru_df['MON']<=end_year)&(output_hru_df['MON']>=begin_year)]
    output_hru_year["AREAkm2"] = output_hru_year["AREAkm2"]/basin_area
    
    year_seq = np.arange(begin_year,end_year+1 , 1)
    SYLD_y = pd.DataFrame()
    SYLD_y['Year'] = year_seq
    par = "SYLD/t/ha"
    unit = par.split('/')[1]
    unit1 = par.split('/')[2]
    
    output_hru_year[par] = output_hru_year["AREAkm2"]*output_hru_year[par]
    par_y = pd.pivot_table(output_hru_year,index=['MON'],values = par, aggfunc="sum")
    SYLD_y[par] = par_y[par].tolist()
    SYLD_y.to_csv(out_path+'/SYLD_Basin_Year.csv',sep=',',index=False,header=True)
    
    if flag==1:
        fig,ax=plt.subplots(figsize=(4,3),sharex=False, sharey=False)
        print('plotting SYLD basin year trend...')
        year = SYLD_y['Year']
        par_y = SYLD_y[par]
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
        ax.set(ylabel = par)
        plt.rcParams['font.size']=12
        plt.rcParams['font.family']='arial'
        plt.rcParams['xtick.labelsize']=12
        plt.rcParams['ytick.labelsize']=12
        plt.rcParams['xtick.major.pad']=8
        plt.rcParams['ytick.major.pad']=8
        plt.tight_layout()
        plt.savefig(out_path+'/SYLD_Basin_Year.tif',bbox_inches='tight',dpi=300)
        
    #SUB尺度计算
    output_sub_df,sub_num = read_SWAT_output_sub(folder_path)
    output_sub_year = output_sub_df[(output_sub_df['MON']<=end_year)&(output_sub_df['MON']>=begin_year)]
    SYLD_sub_mean_slope = pd.DataFrame()
    SYLD_sub_mean_slope["Subbasin"] = np.arange(1,sub_num+1,1)
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
#     par_year_sub.to_csv(out_path+'NPP_Sub_ny.csv',sep=',',index=False,header=True)    
    par_sub = par_year_sub[[par_name+"_ymean",par_name+"_yslope","Subbasin"]]
    SYLD_sub_mean_slope = SYLD_sub_mean_slope.merge(par_sub,on = 'Subbasin', how = 'left')
    SYLD_sub_mean_slope.to_csv(out_path+'/SYLD_Sub_mean_slope.csv',sep=',',index=False,header=True)    
    
    if flag ==1:
        data = SYLD_sub_mean_slope
        data_geod = gp.GeoDataFrame(data)
        sub_shp=folder_path+"/Watershed/Shapes/subs1.shp"
        sub_geom  = gp.GeoDataFrame.from_file(sub_shp, encoding = 'gb18030')
        sub_data = sub_geom.merge(data_geod, on = 'Subbasin', how = 'left')
        fig,ax=plt.subplots(nrows=1, ncols=2,figsize=(6*2,4),sharex=False,sharey=False)
        print('plotting sub space distribution...')
        par0 = par.split('/')[0]
        bins1,nbin1 = d_bins(data[par_name+"_ymean"])
        bins1 = np.round(bins1,0)
        cmap1 = cm.get_cmap('Spectral', nbin1)
        norm1 = mcolors.BoundaryNorm(bins1, nbin1)
        sub_data.plot(par0+"_ymean",ax = ax[0], k=12,norm  = norm1,cmap = cmap1)
        ax[0].axis('off')
        im1 = cm.ScalarMappable(norm=norm1, cmap= cmap1)
        cbar1 = fig.colorbar(
            im1, ax=ax[0], orientation='horizontal',
            shrink=0.5,pad = 0,
            label= par
            )
        bins2,nbin2 = d_bins(data[par_name+"_yslope"])
        bins2 = np.round(bins2,1)
        cmap2 = cm.get_cmap('PiYG', nbin2)
        norm2 = mcolors.BoundaryNorm(bins2, nbin2)
        sub_data.plot(par0+"_yslope",ax = ax[1], k=12,norm  = norm2,cmap = cmap2)
        ax[1].axis('off')
        im2 = cm.ScalarMappable(norm=norm2, cmap= cmap2)
        cbar2 = fig.colorbar(
            im2, ax=ax[1], orientation='horizontal',
            shrink=0.5,pad = 0,
            label= par_name+" trend "+unit+"/"+unit1+" y"
            )
        plt.rcParams['font.size']=12
        plt.rcParams['font.family']='arial'
        plt.subplots_adjust(wspace=-0.15,hspace=0)
        plt.savefig(out_path+'/SYLD_Sub_distribution.tif',bbox_inches='tight',dpi=300)
    
    #HRU尺度计算
    output_hru_year = output_hru_df[(output_hru_df['MON']<=end_year)&(output_hru_df['MON']>=begin_year)]
    SYLD_hru_mean_slope = pd.DataFrame()
    SYLD_hru_mean_slope["HRU_ID"] = np.arange(1,hru_num+1,1)
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
#     par_year_hru.to_csv(out_path+'SYLD_Hru_ny.csv',sep=',',index=False,header=True)
    par_hru = par_year_hru[[par_name+"_ymean",par_name+"_yslope","HRU_ID"]]
    SYLD_hru_mean_slope = SYLD_hru_mean_slope.merge(par_hru,on = 'HRU_ID', how = 'left')
    SYLD_hru_mean_slope.to_csv(out_path+'/SYLD_Hru_mean_slope.csv',sep=',',index=False,header=True)
    
    if flag==1:
        data = SYLD_hru_mean_slope
        data_geod = gp.GeoDataFrame(data)
        hru_shp=folder_path+"/Watershed/Shapes/hru1.shp"
        hru_geom  = gp.GeoDataFrame.from_file(hru_shp, encoding = 'gb18030')
        hru_data = hru_geom.merge(data_geod, on = 'HRU_ID', how = 'left')
        fig,ax=plt.subplots(nrows=1, ncols=2,figsize=(6*2,4),sharex=False,sharey=False)
        print('plotting hru space distribution...')
        par0 = par.split('/')[0]
        bins1,nbin1 = d_bins(data[par_name +"_ymean"])
        bins1 = np.round(bins1,0)
        cmap1 = cm.get_cmap('Spectral', nbin1)
        norm1 = mcolors.BoundaryNorm(bins1, nbin1)
        hru_data.plot(par0+"_ymean",ax = ax[0], k=12,norm  = norm1,cmap = cmap1)
        ax[0].axis('off')
        im1 = cm.ScalarMappable(norm=norm1, cmap= cmap1)
        cbar1 = fig.colorbar(
            im1, ax=ax[0], orientation='horizontal',
            shrink=0.5,pad = 0,
            label= par
            )

        bins2,nbin2 = d_bins(data[par_name+"_yslope"])
        bins2 = np.round(bins2,1)
        cmap2 = cm.get_cmap('PiYG', nbin2)
        norm2 = mcolors.BoundaryNorm(bins2, nbin2)
        hru_data.plot(par0+"_yslope",ax = ax[1], k=12,norm  = norm2,cmap = cmap2)
        ax[1].axis('off')
        im2 = cm.ScalarMappable(norm=norm2, cmap= cmap2)
        cbar2 = fig.colorbar(
            im2, ax=ax[1], orientation='horizontal',
            shrink=0.5,pad = 0,
            label= par_name+" trend "+unit+"/"+unit1+" y"
            )
        plt.rcParams['font.size']=12
        plt.rcParams['font.family']='arial'
        plt.subplots_adjust(wspace=-0.15,hspace=0)
        plt.savefig(out_path+'/SYLD_Hru_distribution.tif',bbox_inches='tight',dpi=300)
        
    
#土壤侵蚀模块M2
def SDR(inputdir,SDR_outputdir):
    if not os.path.exists(SDR_outputdir+'/SDR_result'):
        os.makedirs(SDR_outputdir+'/SDR_result')
    lulc_dir = inputdir+"/"+"Lulc_Folder"
    ero_dir = inputdir+"/"+"Erosivity_Folder"
    file_list = os.listdir(lulc_dir)
    for i in file_list:
        if os.path.splitext(i)[1] == '.tif':
            args = {
                'biophysical_table_path': inputdir+"/"+'biophycial.csv',
                'dem_path': inputdir+"/"+ 'DEM.tif',
                'drainage_path': '',
                'erodibility_path': inputdir+"/"+ 'Soil_K.tif',
                'erosivity_path': ero_dir + "/" + i[:-4]+"Ero"+".tif",
                'ic_0_param': '0.5',
                'k_param': '2',
                'lulc_path': lulc_dir + "/" + i,
                'results_suffix': '',
                'sdr_max': '0.8',
                'threshold_flow_accumulation': '900',
                'watersheds_path': inputdir+'watershed.shp',
                'workspace_dir': SDR_outputdir+'/SDR_result'+"/"+ i[:-4],
                }
            natcap.invest.sdr.sdr.execute(args)
            
def SDR_time_and_space_plot(inputdir,SDR_outputdir,result_outdir):
#     SDR(inputdir,SDR_outputdir)
    SDR_dir = SDR_outputdir+'/SDR_result'
    SDR_year = []
    folder_list =  os.listdir(SDR_dir)
    x = np.arange(1,len(folder_list)+1,1)
    tif_dir = SDR_dir +"/"+folder_list[0] +"/"+"sed_export.tif"
    tif = xr.open_rasterio(tif_dir)
    tif = tif[0]
    #   Define extents
    lat_min = tif.y.min()
    lat_max = tif.y.max()
    lon_min = tif.x.min()
    lon_max = tif.x.max()
    extent = [lon_min, lon_max, lat_min, lat_max] # [left, right, bottom, top]
    im_proj = read_rasterfile(tif_dir)[5]
    proj1 = Proj(im_proj)
    x_min,y_min=  proj1(lon_min,lat_min,inverse = True)
    x_max,y_max=  proj1(lon_max,lat_max,inverse = True)
    array = read_rasterfile(tif_dir)[0]
    array[:][:] = 0.0
    for i in os.listdir(SDR_dir):     
        SDR_raster = SDR_dir +"/"+i+"/"+"sed_export.tif"
        SDR_tif = read_rasterfile(SDR_raster)[0]
        #数据
        SDR_tif = np.where(SDR_tif  == -1, np.nan, SDR_tif )
        SDR_year.append(np.nanmean(SDR_tif))
        array = array+SDR_tif
    array = array/float(len(os.listdir(SDR_dir)))
    array = np.where(array == -1, np.nan, array)
    fig = plt.figure(figsize=(8,6),dpi=50)
    m = Basemap(llcrnrlon=x_min, llcrnrlat=y_min, urcrnrlon=x_max, urcrnrlat=y_max, # 左下右上经纬度坐标 关键在于如何将已投影的坐标转换为经纬度坐标
                projection='aea', # albers等面积投影
                resolution='h', lat_0=0, lon_0=105, lat_1=25, lat_2=47)

    norm = matplotlib.colors.Normalize(vmin=0, vmax=int(np.nanmax(array))+1)
    m.imshow(array, origin='upper', extent=extent, cmap='coolwarm', norm=norm) # 绘制栅格数据

    cb = m.colorbar(extend='both' ,location="bottom", pad=0.3) 
    cb.ax.tick_params(labelsize=16)  #设置色标刻度字体大小。
    cb.set_label("sed_export/t")
    parallels = np.arange(int(y_min),int(y_max),0.5) # 绘制经纬度线
    meridians = np.arange(int(x_min),int(x_max),0.5)
    m.drawparallels(parallels,labels=[True,False,False,False], linewidth=0.1) # labels = [left,right,top,bottom]
    m.drawmeridians(meridians,labels=[False,False,False,True], linewidth=0.1)
    plt.rcParams['font.size']=16
    plt.rcParams['font.family']='arial'
    plt.savefig(result_outdir+"/SDR_space.tif",bbox_inches='tight',dpi=300)

    fig = plt.figure(figsize=(4,3),dpi=50)
    plt.ylim(np.min(SDR_year)*0.5, np.max(SDR_year)*1.2)
    plt.ylabel("sed_export/t")
    plt.xticks(x)
    plt.bar(x,SDR_year,color='skyblue',width=0.4)
    plt.rcParams['font.size']=16
    plt.rcParams['font.family']='arial'
    plt.savefig(result_outdir+"/SDR_year.tif",bbox_inches='tight',dpi=300)
    
    out_tif_name = result_outdir+"/SDR_ny_mean_result.tif"
    driver = gdal.GetDriverByName("GTiff")
    out_tif = driver.Create(out_tif_name, read_rasterfile(tif_dir)[1], read_rasterfile(tif_dir)[2], 1, gdal.GDT_Float32)
    geotransform = read_rasterfile(tif_dir)[4]
    out_tif.SetGeoTransform(geotransform)        
    srs = osr.SpatialReference()
    proj_type = read_rasterfile(tif_dir)[5]
    out_tif.SetProjection(proj_type)  
    # 数据写出        
    out_tif.GetRasterBand(1).WriteArray(array)  
    out_tif.FlushCache()  # 将数据写入硬盘
    out_tif = None  # 注意必须关闭tif文件
    print("Multi-year average SDR calculating finish!")
    
#碳储存模块
#M1:
#DayCent Model output analysis
def read_DayCent_output(folder_path):    
    CENT_output_path = folder_path+"/TxtInOut/CENT/CENT_year.out"
    CENT_output_data = pd.read_table(CENT_output_path,sep ='\s+')
    hru_num = CENT_output_data["iHRU"].tolist()[-1]
    sub_num = CENT_output_data["iSUB"].tolist()[-1]
    return CENT_output_data,hru_num,sub_num

def Cent_output_NPP(folder_path,begin_year,end_year,out_path,flag):
    CENT_output_data,hru_num,sub_num = read_DayCent_output(folder_path)
    year_seq = np.arange(begin_year,end_year+1 , 1)
    CENT_hru_year = CENT_output_data[(CENT_output_data['Y']<=end_year)&(CENT_output_data['Y']>=begin_year)]
    # 年尺度
    NPP_y = pd.DataFrame()
    NPP_y['Year'] = year_seq
    par = "cproda"
    par_y = pd.pivot_table(CENT_hru_year,index=['Y'],values = par, aggfunc="mean")
    NPP_y[par] = par_y[par].tolist()
    NPP_y.to_csv(out_path+'/NPP_Basin_Year.csv',sep=',',index=False,header=True)
    
    #HRU尺度
    NPP_hru_mean_slope = pd.DataFrame()
    NPP_hru_mean_slope["HRU_ID"] = np.arange(1,hru_num+1,1)
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
#     par_year_hru.to_csv(out_path+'NPP_Hru_ny.csv',sep=',',index=False,header=True)
    par_hru = par_year_hru[[par_name+"_ymean",par_name+"_yslope","HRU_ID"]]
    NPP_hru_mean_slope = NPP_hru_mean_slope.merge(par_hru,on = 'HRU_ID', how = 'left')
    NPP_hru_mean_slope.to_csv(out_path+'/NPP_Hru_mean_slope.csv',sep=',',index=False,header=True)
    
    #SUB尺度
    CENT_sub_year = CENT_output_data[(CENT_output_data['Y']<=end_year)&(CENT_output_data['Y']>=begin_year)]
    NPP_sub_mean_slope = pd.DataFrame()
    NPP_sub_mean_slope["Subbasin"] = np.arange(1,sub_num+1,1)
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
#     par_year_sub.to_csv(out_path+'NPP_Sub_ny.csv',sep=',',index=False,header=True)    
    par_sub = par_year_sub[[par_name+"_ymean",par_name+"_yslope","Subbasin"]]
    NPP_sub_mean_slope = NPP_sub_mean_slope.merge(par_sub,on = 'Subbasin', how = 'left')
    NPP_sub_mean_slope.to_csv(out_path+'/NPP_Sub_mean_slope.csv',sep=',',index=False,header=True)    
    
    if flag ==1:
        fig,ax=plt.subplots(figsize=(4,3),sharex=False, sharey=False)
        print('plotting NPP...')      
        year = NPP_y['Year']
        par_y = NPP_y[par]
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
        ax.set(ylabel = par)
        plt.rcParams['font.size']=12
        plt.rcParams['font.family']='arial'
        plt.rcParams['xtick.labelsize']=12
        plt.rcParams['ytick.labelsize']=12
        plt.rcParams['xtick.major.pad']=8
        plt.rcParams['ytick.major.pad']=8
        plt.tight_layout()    
        plt.savefig(out_path+'/NPP_Basin_Year.tif',bbox_inches='tight',dpi=300)  
        
        data = NPP_hru_mean_slope
        data_geod = gp.GeoDataFrame(data)
        hru_shp=folder_path+"/Watershed/Shapes/hru1.shp"
        hru_geom  = gp.GeoDataFrame.from_file(hru_shp, encoding = 'gb18030')
        hru_data = hru_geom.merge(data_geod, on = 'HRU_ID', how = 'left')
        fig,ax=plt.subplots(nrows=1, ncols=2,figsize=(6*2,4),sharex=False,sharey=False)
        par0 = par.split('/')[0]
        bins1,nbin1 = d_bins(data[par0+"_ymean"])
        bins1 = np.round(bins1,0)
        cmap1 = cm.get_cmap('Spectral', nbin1)
        norm1 = mcolors.BoundaryNorm(bins1, nbin1)
        hru_data.plot(par0+"_ymean",ax = ax[0], k=12,norm  = norm1,cmap = cmap1)
        ax[0].axis('off')
        im1 = cm.ScalarMappable(norm=norm1, cmap= cmap1)
        cbar1 = fig.colorbar(
            im1, ax=ax[0], orientation='horizontal',
            shrink=0.5,pad = 0,
            label= par
            )

        bins2,nbin2 = d_bins(data[par+"_yslope"])
        bins2 = np.round(bins2,1)
        cmap2 = cm.get_cmap('PiYG', nbin2)
        norm2 = mcolors.BoundaryNorm(bins2, nbin2)
        hru_data.plot(par0+"_yslope",ax = ax[1], k=12,norm  = norm2,cmap = cmap2)
        ax[1].axis('off')
        im2 = cm.ScalarMappable(norm=norm2, cmap= cmap2)
        cbar2 = fig.colorbar(
            im2, ax=ax[1], orientation='horizontal',
            shrink=0.5,pad = 0,
            label= par0+" trend"
            )
        plt.rcParams['font.size']=12
        plt.rcParams['font.family']='arial'
        plt.subplots_adjust(wspace=-0.15,hspace=0)
        plt.savefig(out_path+'/NPP_Hru_distribution.tif',bbox_inches='tight',dpi=300)

        data = NPP_sub_mean_slope
        data_geod = gp.GeoDataFrame(data)
        sub_shp=folder_path+"/Watershed/Shapes/subs1.shp"
        sub_geom  = gp.GeoDataFrame.from_file(sub_shp, encoding = 'gb18030')
        sub_data = sub_geom.merge(data_geod, on = 'Subbasin', how = 'left')
        fig,ax=plt.subplots(nrows=1, ncols=2,figsize=(6*2,4),sharex=False,sharey=False)
        print('plotting sub space distribution...')
        par0 = par.split('/')[0]
        bins1,nbin1 = d_bins(data[par0+"_ymean"])
        bins1 = np.round(bins1,0)
        cmap1 = cm.get_cmap('Spectral', nbin1)
        norm1 = mcolors.BoundaryNorm(bins1, nbin1)
        sub_data.plot(par0+"_ymean",ax = ax[0], k=12,norm  = norm1,cmap = cmap1)
        ax[0].axis('off')
        im1 = cm.ScalarMappable(norm=norm1, cmap= cmap1)
        cbar1 = fig.colorbar(
            im1, ax=ax[0], orientation='horizontal',
            shrink=0.5,pad = 0,
            label= par
            )
        bins2,nbin2 = d_bins(data[par+"_yslope"])
        bins2 = np.round(bins2,1)
        cmap2 = cm.get_cmap('PiYG', nbin2)
        norm2 = mcolors.BoundaryNorm(bins2, nbin2)
        sub_data.plot(par0+"_yslope",ax = ax[1], k=12,norm  = norm2,cmap = cmap2)
        ax[1].axis('off')
        im2 = cm.ScalarMappable(norm=norm2, cmap= cmap2)
        cbar2 = fig.colorbar(
            im2, ax=ax[1], orientation='horizontal',
            shrink=0.5,pad = 0,
            label= par0+" trend"
            )
        plt.rcParams['font.size']=12
        plt.rcParams['font.family']='arial'
        plt.subplots_adjust(wspace=-0.15,hspace=0)
        plt.savefig(out_path+'/NPP_Sub_distribution.tif',bbox_inches='tight',dpi=300)
           
#碳储量M2:
def carbon(inputdir,carbon_outputdir):
    if not os.path.exists(carbon_outputdir+'/HQ_result'):
        os.makedirs(carbon_outputdir+'/HQ_result')
#     os.mkdir(deg_outputdir+'HQ_result')
    lulc_dir = inputdir+"/"+"Lulc_Folder"
    file_list = os.listdir(lulc_dir)
    for i in file_list:
        if os.path.splitext(i)[1] == '.tif':
            args = {       
                'calc_sequestration': False,
                'carbon_pools_path':inputdir+"/"+"carbon_pools.csv",
                'do_redd': False,
                'do_valuation': False,
                'lulc_cur_path': lulc_dir + "/" + i,
                'results_suffix': '',
                'workspace_dir': carbon_outputdir+'/HQ_result'+"/"+ i[:-4],
                }
            natcap.invest.carbon.execute(args)
            
def carbon_time_and_space_plot(inputdir,carbon_outputdir,result_outdir):
    carbon(inputdir,carbon_outputdir)
    carbon_dir = carbon_outputdir+'/HQ_result'
    carbon_year = []
    folder_list =  os.listdir(carbon_dir)
    x = np.arange(1,len(folder_list)+1,1)
    tif_dir = carbon_dir +"/"+folder_list[0] +"/"+"tot_c_cur.tif"
    tif = xr.open_rasterio(tif_dir)
    tif = tif[0]
    #   Define extents
    lat_min = tif.y.min()
    lat_max = tif.y.max()
    lon_min = tif.x.min()
    lon_max = tif.x.max()
    extent = [lon_min, lon_max, lat_min, lat_max] # [left, right, bottom, top]
    im_proj = read_rasterfile(tif_dir)[5]
    proj1 = Proj(im_proj)
    x_min,y_min=  proj1(lon_min,lat_min,inverse = True)
    x_max,y_max=  proj1(lon_max,lat_max,inverse = True)
    array = read_rasterfile(tif_dir)[0]
    array[:][:] = 0.0
    for i in os.listdir(carbon_dir):     
        carbon_raster = carbon_dir +"/"+i+"/"+"tot_c_cur.tif"
        carbon_tif = read_rasterfile(carbon_raster)[0]
        #数据
        carbon_tif = np.where(carbon_tif  == -1, np.nan, carbon_tif )
        carbon_year.append(np.nanmean(carbon_tif))
        array = array+carbon_tif
    array = array/float(len(os.listdir(carbon_dir)))
    array = np.where(array == -1, np.nan, array)
    fig = plt.figure(figsize=(8,6),dpi=50)
    m = Basemap(llcrnrlon=x_min, llcrnrlat=y_min, urcrnrlon=x_max, urcrnrlat=y_max, # 左下右上经纬度坐标 关键在于如何将已投影的坐标转换为经纬度坐标
                projection='aea', # albers等面积投影
                resolution='h', lat_0=0, lon_0=105, lat_1=25, lat_2=47)

    norm = matplotlib.colors.Normalize(vmin=0, vmax=int(np.nanmax(array))+1)
    m.imshow(array, origin='upper', extent=extent, cmap='coolwarm', norm=norm) # 绘制栅格数据

    cb = m.colorbar(extend='both' ,location="bottom", pad=0.3) 
    cb.ax.tick_params(labelsize=16)  #设置色标刻度字体大小。
    cb.set_label("total carbon/t/ha")
    parallels = np.arange(int(y_min),int(y_max),0.5) # 绘制经纬度线
    meridians = np.arange(int(x_min),int(x_max),0.5)
    m.drawparallels(parallels,labels=[True,False,False,False], linewidth=0.1) # labels = [left,right,top,bottom]
    m.drawmeridians(meridians,labels=[False,False,False,True], linewidth=0.1)
    plt.rcParams['font.size']=16
    plt.rcParams['font.family']='arial'
    plt.savefig(result_outdir+"/carbon_space.tif",bbox_inches='tight',dpi=300)

    fig = plt.figure(figsize=(4,3),dpi=50)
    plt.ylim(np.min(carbon_year)*0.5, np.max(carbon_year)*1.2)
    plt.ylabel("total carbon/t/ha")
    plt.xticks(x)
    plt.bar(x,carbon_year,color='skyblue',width=0.4)
    plt.rcParams['font.size']=16
    plt.rcParams['font.family']='arial'
    plt.savefig(result_outdir+"/carbon_year.tif",bbox_inches='tight',dpi=300)
    
    out_tif_name = result_outdir+"/carbon_ny_mean_result.tif"
    driver = gdal.GetDriverByName("GTiff")
    out_tif = driver.Create(out_tif_name, read_rasterfile(tif_dir)[1], read_rasterfile(tif_dir)[2], 1, gdal.GDT_Float32)
    geotransform = read_rasterfile(tif_dir)[4]
    out_tif.SetGeoTransform(geotransform)        
    srs = osr.SpatialReference()
    proj_type = read_rasterfile(tif_dir)[5]
    out_tif.SetProjection(proj_type)  
    # 数据写出        
    out_tif.GetRasterBand(1).WriteArray(array)  
    out_tif.FlushCache()  # 将数据写入硬盘
    out_tif = None  # 注意必须关闭tif文件
    print("Multi-year average carbon calculating finish!")
    
    
if __name__ == '__main__':
    model_id = int(sys.argv[1])
    #model_id = 2
    if model_id==1:
        folder_path = sys.argv[2]
        begin_year = int(sys.argv[3])
        end_year = int(sys.argv[4])
        out_path = sys.argv[5]
        flag = int(sys.argv[6])
        print(folder_path)
        print(begin_year)
        print(end_year)
        print(out_path)
        print(flag)
        #folder_path = "D:/SWAT_Daycent_software_test/Water_Retention/WR1"
        #begin_year = 1980
        #end_year = 2019  
        #out_path = "D:/SWAT_Daycent_software_test/Water_Retention/WR1"
        #flag = 1
        WR1_output(folder_path,begin_year,end_year,out_path,flag)
        print('finished!')
    elif model_id==2:
        dem_dir = sys.argv[2]
        watershed_dir = sys.argv[3]
        Ksat_dir = sys.argv[4]
        Vel_dir = sys.argv[5]
        folder_path = sys.argv[6]
        output_dir = sys.argv[7]
        begin_year = int(sys.argv[8])
        end_year = int(sys.argv[9])
        flag = int(sys.argv[10])
        print(dem_dir)
        print(watershed_dir)
        print(Ksat_dir)
        print(Vel_dir)
        print(folder_path)
        print(output_dir)
        print(begin_year)
        print(end_year)
        print(flag)
        #dem_dir = r'D:\SWAT_Daycent_software_test\Water_Retention\WR2\DEM\DYK_DEM.tif'
        #watershed_dir = r'D:\SWAT_Daycent_software_test\Water_Retention\WR2\Watershed'
        #Ksat_dir = r"D:\SWAT_Daycent_software_test\Water_Retention\WR2\Soil_Ksat.csv"
        #Vel_dir = r"D:\SWAT_Daycent_software_test\Water_Retention\WR2\Vel_coef.csv"
        #folder_path = "D:\SWAT_Daycent_software_test\Water_Retention\WR2"
        #output_dir = r"D:\SWAT_Daycent_software_test\Water_Retention\WR2\output_dir"
        #begin_year = 1980
        #end_year = 2019
        #flag = 1
        WR2_output(dem_dir,watershed_dir,Ksat_dir,Vel_dir,folder_path,begin_year,end_year,output_dir,flag)
        print('finished!')
    elif model_id==3:
        folder_path = sys.argv[2]
        begin_year = int(sys.argv[3])
        end_year = int(sys.argv[4])
        out_path = sys.argv[5]
        flag = int(sys.argv[6])
        print(folder_path)
        print(begin_year)
        print(end_year)
        print(out_path)
        print(flag)
        #folder_path = "D:/SWAT_Daycent_software_test/Soil_Erosion/Soil_Ero_M1"
        #begin_year = 2000
        #end_year = 2019  
        #out_path = "D:/SWAT_Daycent_software_test/Soil_Erosion/Soil_Ero_M1"
        #flag = 1
        SWAT_output_syld(folder_path,begin_year,end_year,out_path,flag)
        print('finished!')
    elif model_id==4:
        inputdir = sys.argv[2]
        SDR_outputdir = sys.argv[3]
        result_outdir = sys.argv[4]
        print(inputdir)
        print(SDR_outputdir)
        print(result_outdir)
        #inputdir ="D:/SWAT_Daycent_software_test/Soil_Erosion/Soil_Ero_M2"
        #SDR_outputdir = "D:/SWAT_Daycent_software_test/Soil_Erosion/Soil_Ero_M2"
        #result_outdir = "D:/SWAT_Daycent_software_test/Soil_Erosion/Soil_Ero_M2"
        SDR_time_and_space_plot(inputdir,SDR_outputdir,result_outdir)
        print('finished!')
    elif model_id==5:
        folder_path = sys.argv[2]
        begin_year = int(sys.argv[3])
        end_year = int(sys.argv[4])
        out_path = sys.argv[5]
        flag = int(sys.argv[6])
        print(folder_path)
        print(begin_year)
        print(end_year)
        print(out_path)
        print(flag)
        #folder_path = "D:/SWAT_Daycent_software_test/Carbon_cal/Carbon_M1"
        #begin_year = 2000
        #end_year = 2019  
        #out_path = "D:/SWAT_Daycent_software_test/Carbon_cal/Carbon_M1"
        #flag = 1
        Cent_output_NPP(folder_path,begin_year,end_year,out_path,flag)
        print('finished!')
    elif model_id==6:
        inputdir = sys.argv[2]
        carbon_outputdir = sys.argv[3]
        result_outdir = sys.argv[4]
        print(inputdir)
        print(carbon_outputdir)
        print(result_outdir)
        #inputdir ="D:/SWAT_Daycent_software_test/Carbon_cal/Carbon_M2"
        #carbon_outputdir = "D:/SWAT_Daycent_software_test/Carbon_cal/Carbon_M2"
        #result_outdir = "D:/SWAT_Daycent_software_test/Carbon_cal/Carbon_M2"
        carbon_time_and_space_plot(inputdir,carbon_outputdir,result_outdir)
        print('finished!')