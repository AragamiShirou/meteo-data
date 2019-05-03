from netCDF4 import Dataset
from datetime import datetime, timedelta
import numpy as np
from netCDF4 import date2num
from scipy.stats import ttest_ind as ttest
from ncread import ncdata
from ncread1 import ncdata as nd

def ncwrite(filename, lons, lats, levs, data, varname, desc, calendar_type, units, missing_value):
    "'write nc_file: \n\
        desc: descriptions of the file\n\
        units: var unit \n\
        missing_value: value for mask NAN'"
    dim_t, dim_lev, dim_lat, dim_lon = data.shape
    dataset = Dataset(filename, 'w', format='NETCDF4_CLASSIC')
    level = dataset.createDimension('level', dim_lev)
    lat = dataset.createDimension('lat', dim_lat)
    lon = dataset.createDimension('lon', dim_lon)
    time = dataset.createDimension('time', None)
    # coordinate variables
    times = dataset.createVariable('time', np.float64, ('time',))
    levels = dataset.createVariable('level', np.float32, ('level',))
    latitudes = dataset.createVariable('lat', np.float32, ('lat',))
    longitudes = dataset.createVariable('lon', np.float32, ('lon',))
    # 4-D variable
    var = dataset.createVariable(varname, np.float32,
                               ('time', 'level', 'lat', 'lon'))

    dataset.description = desc
    # ##debug
    # for varname in dataset.variables.keys():
    #    var = dataset.variables[varname]
    #    print(varname, var.dtype, var.dimensions, var.shape)

    # variable attributes
    latitudes.units = 'degree_north'
    longitudes.units = 'degree_east'
    levels.units = 'hPa'
    var.units = units
    var.missing_value=missing_value
    times.units = 'hour since 1948-01-01 00:00:00'
    times.calendar = calendar_type

    # writing data
    levels[:] = levs
    latitudes[:] = lats
    longitudes[:] = lons
    var[0:dim_t, :, :, :] = data

    # fill in times
    datess = []
    for n in range(data.shape[0]):
        datess.append(datetime(1, 1, 1) + n * timedelta(hours=24))
    times[:] = date2num(datess, units=times.units, calendar=times.calendar)
    # print('lat=\n', latitudes[:])
    # print('lon=\n',longitudes[:])
    dataset.close()

def get_dims(dtype,var):
    nc0=Dataset("D:\\data\\"+dtype+"\\"+var+".1978.nc")
    levs=nc0.variables["lev"][:]
    nlev1000=np.argmin(abs(levs-1000))
    nlev10=np.argmin(abs(levs-10))
    lat=nc0.variables['lat'][:]
    nlat60=np.argmin(abs(lat-60))
    levb_i=min(nlev1000,nlev10)
    leve_i=max(nlev1000,nlev10)
    lon0=nc0.variables["lon"][:]
    nc0.close()
    return levb_i, leve_i, nlat60

def get_mean(dtype,var):
    fname=fpath00+var+".mean."+dtype+".nc"
    nc=Dataset(fname)
    means=np.squeeze(nc.variables[var][:,:,:])
    nc.close()
    return means

def get_sswdate(dtype):
    fdate=fpath00+dtype+".txt"
    with open(fdate) as fobj:
        lines=fobj.readlines()
    return lines

def calculate_anoma(dtype,var,mon):
    # calculate the anomalies(anoma) of SSW in NDJ or FM,
    # while tdata is the NCEP1 or Model real data of the stage.
    # test_t is the t-test  properties for real data and month climatology if significant.
    lonb = 0
    lone = 360
    latb = 60
    late = 60
    levb = 1000
    leve = 10
    umean=get_mean(dtype,var)
    #mons=np.array(["11","12","01"],["02","22","03"])
    #for im in range(2):
    sswdates=np.zeros(shape=50,dtype="<U12")
    lines=get_sswdate(dtype)
    #    mon=np.int16(mons[im])
    k=0
    for line in lines:
        if (np.int16(line[5:7])==mon[0] or np.int16(line[5:7])==mon[1] or np.int16(line[5:7])==mon[2]):
            sswdates[k]=line
            k=k+1
    sswdates=sswdates[np.argwhere(sswdates != "").squeeze()]

    anoma=np.zeros(shape=[121,17,1,1],dtype="float32")
    test_t=np.zeros(shape=[121,17,1,1],dtype="float32")
    tstat=np.zeros(shape=[121,17,1,1],dtype="float32")
    ik=1

    tdata=np.zeros(shape=[121,17,sswdates.size],dtype="float32")
    sdata=np.zeros(shape=[121,17,sswdates.size],dtype="float32")
    stg=np.zeros(shape=[121,sswdates.size],dtype="U<12")
        
    fpath="D:\\data\\"+dtype+"\\"+var+"."
    for sswdate in sswdates:
        year=sswdate[0:4]
        fname=fpath+year+".nc"
        dset = ncdata(fname,np.int32(year))
        id_center=np.argwhere(dset.date==sswdate[0:10]).squeeze()
        id_tb=id_center-60
        id_te=id_center+60
        # mae ni
        if id_tb<0:
            year1=np.int16(year)+1
            fname=fpath+str(year1)+".nc"
            dset1=ncdata(fname,year1)
            tb1=dset1.date[id_tb]
            te1=dset1.date[-1]
            dset1.get_var(lonb,lone,latb,late,levb,leve,tb1,te1,var)
            hgt1=np.nanmean(dset1.var,axis=3)
            date1=dset1.date[id_te]
            dset1.close()

            tb2=dset.date[0]
            te2=dset.date[id_te]
            dset.get_var(lonb,lone,late,levb,leve,tb1,te1,var)
            hgt2=np.nanmean(dset.var,axis=3)

            date2=dset.date[:id_te+1]
            hgt0=np.concatenate((hgt1,hgt2))
            date0=np.concatenate((date1,date2))
        # ushiro ni
        elif id_te>=dset.totalday:
            # 现年数据提取
            tb1 = dset.date[id_tb]
            te1 = dset.date[-1]
            dset.get_var(lonb, lone, latb, late, levb, leve, tb1, te1, var)
            hgt1 = np.nanmean(dset.var, axis=3)
            date1 = dset.date[id_tb:]

            # 后年数据提取
            year1 = np.int16(year) + 1
            fname = fpath + str(year1) + ".nc"
            dset1 = ncdata(fname, np.int32(year1))
            tb2 = dset1.date[0]
            te2 = dset1.date[id_te - dset.totalday]
            dset1.get_var(lonb, lone, latb, late, levb, leve, tb2, te2, var)
            hgt2 = np.nanmean(dset1.var,axis=3)
            date2 = dset1.date[:id_te - dset.totalday + 1]
            dset1.fclose()

            hgt0 = np.concatenate((hgt1, hgt2))
            date0 = np.concatenate((date1, date2))
        # only one year
        else:
            tb=dset.date[id_tb]
            te=dset.date[id_te]
            dset.get_var(lonb, lone, latb, late, levb, leve, tb1, te1, var)
            hgt0=np.nanmean(dset.var,axis=3)
            date0=dset.date[id_tb:id_te+1]
            
        hgt0=hgt0.reshape(121,17)
        ########
        tdata[:,:,ik-1]=hgt0
        ########

        # 异常合成
        for i in np.arange(121):
            m = np.int32(date0[i][5:7])
            u_a = hgt0[i, :].reshape(17,1) - umean[m - 1, :].reshape(17, 1)
            anoma[i, :, :, :] = anoma[i, :, :, :] * (ik - 1) / ik + u_a.reshape(1, 17, 1, 1) / ik
            #tdata[i, :, ik - 1] = anoma[i, :, :, :].reshape(17)
            stg[i, ik - 1] = m
            sdata[i,:,ik-1] = umean[m-1,:]
        dset.fclose()
        ik = ik + 1

    # -------t 检验------------#

        s2 = np.zeros(shape=tdata.shape[2])
        for ix in np.arange(tdata.shape[0]):
            for iy in np.arange(tdata.shape[1]):
                tstat[ix, iy, :, :], test_t[ix, iy, :, :] = ttest(tdata[ix, iy, :], sdata[ix, iy, :])

    return anoma,tdata,test_t


# global fpath00
# fpath00="H:\\py3.5\\data\\"

# mons=np.array(["11","12","01"],["02","22","03"])
# anoma_n=np.zeros(shape=[1,17,2,121],dtype="float32")
# pvalur_n=np.zeros(shape=[1,17,2,121],dtype="float32")
# tdata_n
# for im in range(2):
#    mon=np.int16(mons[im])
#    dtype="NCEP"
#    var='hgt'
#    aa,td,tt=calculate_anoma(dtype,var,mon)
#    anoma[:,:,im,:]=aa.reshape(1,17,1,121)
    


# print(get_sswdate("NCEP"))
# print(get_mean("Model","hgt"))
