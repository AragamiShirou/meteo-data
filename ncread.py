import netCDF4
import numpy as np
import calendar


class ncdata():

    def __init__(self, filename):
        self.filename = filename
        self.dataset = netCDF4.Dataset(self.filename)
        self.dataset.set_auto_mask(False)
        time = self.dataset.variables['time'][:]
        self.lat = self.dataset.variables['lat'][:]
        self.lon = self.dataset.variables['lon'][:]
        self.lev = self.dataset.variables['level'][:]
        self.totalday = np.where(calendar.isleap(int(self.filename[5:9])), 366, 365)
        self.month = np.zeros(self.totalday)
        t = time / 24
        self.date = netCDF4.num2date(t, units='days since 1-1-1', calendar='standard')
        #self.var = self.dataset.variables[filename[0:4]][:, :, :, :]#[t, lev, lat, lon]

    def get_month(self):
        for i in range(self.date.__len__()):
            self.month[i] = int(str(self.date[i])[5:7])

    def get_var(self, lonb, lone, latb, late, levb, leve):
        idx_lon = np.arange(0, self.lon.__len__(), 1)
        idx_lat = np.arange(0, self.lat.__len__(), 1)
        idx_lev = np.arange(0, self.lev.__len__(), 1)
        idx_lonb = min(idx_lon[np.argmin(abs(self.lon - lonb))], idx_lon[np.argmin(abs(self.lon - lone))])
        idx_lone = max(idx_lon[np.argmin(abs(self.lon - lonb))], idx_lon[np.argmin(abs(self.lon - lone))])
        idx_latb = min(idx_lat[np.argmin(abs(self.lat - latb))], idx_lat[np.argmin(abs(self.lat - late))])
        idx_late = max(idx_lat[np.argmin(abs(self.lat - latb))], idx_lat[np.argmin(abs(self.lat - late))])
        idx_levb = min(idx_lev[np.argmin(abs(self.lev - levb))], idx_lev[np.argmin(abs(self.lev - leve))])
        idx_leve = max(idx_lev[np.argmin(abs(self.lev - levb))], idx_lev[np.argmin(abs(self.lev - leve))])
        self.lon_range = np.arange(idx_lonb, idx_lone+1, 1)
        self.lat_range = np.arange(idx_latb, idx_late+1, 1)
        self.lev_range = np.arange(idx_levb, idx_leve+1, 1)
        self.var = self.dataset.variables[self.filename[0:4]][:, self.lev_range, self.lat_range, self.lon_range]