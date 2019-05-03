import netCDF4
import numpy as np
import calendar


class ncdata():

    def __init__(self, filename, year):
        self.dataset = netCDF4.Dataset(filename)
        # self.dataset.set_auto_mask(False)
        time = self.dataset.variables['time'][:]
        self.lat = self.dataset.variables['lat'][:]
        self.lon = self.dataset.variables['lon'][:]
        varnames=self.dataset.variables
        for vname in varnames:
            if ("lev" in vname):
                levname=vname
                break
        self.lev = self.dataset.variables[levname][:]
        self.totalday = self.dataset.variables['time'][:].__len__()
        self.month = np.zeros(self.totalday)
        self.dt=time[1]-time[0]
        t = time/self.dt
        self.time_units=self.dataset.variables['time'].units
        self.time_calendar=self.dataset.variables['time'].calendar
        self.date0 = netCDF4.num2date(t, units=self.time_units, calendar=self.time_calendar)
        self.date = np.array([self.date0[i].strftime("%Y-%m-%d") for i in np.arange(self.date0.__len__())])
        #self.var = self.dataset.variables[filename[0:4]][:, :, :, :]#[t, lev, lat, lon]

    def get_month(self):
        for i in range(self.date.__len__()):
            self.month[i] = np.int32(str(self.date[i])[5:7])

    def get_var(self, lonb, lone, latb, late, levb, leve, tb, te, varname):
    #    """lonb,lone: 开始,结束经度（0-360）；latb,late:开始,结束纬度（-90-90）；levb,leve:开始,结束高度；tb,te：开始,结束日期（'YYYY-MM-DD'）；varname：变量名称"""
        idx_lon = np.arange(0, self.lon.__len__(), 1)
        idx_lat = np.arange(0, self.lat.__len__(), 1)
        idx_lev = np.arange(0, self.lev.__len__(), 1)
        idx_t = np.arange(0, self.totalday-1, 1)
        idx_lonb = min(idx_lon[np.argmin(abs(self.lon - lonb))], idx_lon[np.argmin(abs(self.lon - lone))])
        idx_lone = max(idx_lon[np.argmin(abs(self.lon - lonb))], idx_lon[np.argmin(abs(self.lon - lone))])
        idx_latb = min(idx_lat[np.argmin(abs(self.lat - latb))], idx_lat[np.argmin(abs(self.lat - late))])
        idx_late = max(idx_lat[np.argmin(abs(self.lat - latb))], idx_lat[np.argmin(abs(self.lat - late))])
        idx_levb = min(idx_lev[np.argmin(abs(self.lev - levb))], idx_lev[np.argmin(abs(self.lev - leve))])
        idx_leve = max(idx_lev[np.argmin(abs(self.lev - levb))], idx_lev[np.argmin(abs(self.lev - leve))])
        idx_tb = np.squeeze(np.argwhere(self.date == tb))
        idx_te = np.squeeze(np.argwhere(self.date == te))
        self.lon_range = np.arange(idx_lonb, idx_lone+1, 1)
        self.lat_range = np.arange(idx_latb, idx_late+1, 1)
        self.lev_range = np.arange(idx_levb, idx_leve+1, 1)
        self.time_range = np.arange(idx_tb, idx_te+1, 1)
        self.var = self.dataset.variables[varname][self.time_range, self.lev_range, self.lat_range, self.lon_range]
        self.units=self.dataset.variables[varname].units
        self.missing_value=self.dataset.variables[varname].missing_value

    def fclose(self):
        self.dataset.close()



