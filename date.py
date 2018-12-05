import netCDF4
import numpy as np
import calendar


class Date():

    def __init__(self, filename):
        dataset = netCDF4.Dataset(filename)
        dataset.set_auto_mask(False)
        self.time = dataset.variables['time'][:]
        self.lat = dataset.variables['lat'][:]
        self.lon = dataset.variables['lon'][:]
        self.lev = dataset.variables['level'][:]
        self.month = np.zeros(np.where(calendar.isleap(int(filename[5:9])), 366, 365))
        t = self.time / 24
        self.date = netCDF4.num2date(t, units='days since 1-1-1', calendar='standard')
        self.var = dataset.variables[filename[0:4]][:, :, :, :]#[t, lev, lat, lon]
        dataset.close()

    def get_month(self):
        for i in range(self.time.__len__()):
            self.month[i] = int(str(self.date[i])[5:7])



