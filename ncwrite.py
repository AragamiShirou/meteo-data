import numpy as np
from netCDF4 import Dataset
from datetime import datetime, timedelta
from netCDF4 import date2num

def ncwrite(filename, lons, lats, levs, data, varname, desc):
    'write nc_file'
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
    ###debug
    # for varname in dataset.variables.keys():
    #    var = dataset.variables[varname]
    #    print(varname, var.dtype, var.dimensions, var.shape)

    # variable attributes
    latitudes.units = 'degree_north'
    longitudes.units = 'degree_east'
    levels.units = 'hPa'
    var.units = 'm/s'
    times.units = 'hour since 1-1-1 00:00:00'
    times.calendar = 'gregorian'

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
