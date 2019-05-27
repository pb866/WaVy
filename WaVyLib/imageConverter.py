#!/usr/bin/env python
import collections
import numpy as np


class ConvertImage:
    def __init__(self, ds):
        self.ds = ds

    def bandNames(self):
        band = ['b'+str(i+1) for i in list(range(self.ds.RasterCount))]
        return band

    def bandsAsNumPy(self):
        band = self.bandNames()
        t = 1
        bands = {}
        for i in band:
            bands[band[t-1]] = self.ds.GetRasterBand(t).ReadAsArray(0, 0, self.ds.RasterXSize, self.ds.RasterYSize)
            t += 1
        bands = collections.OrderedDict(sorted(bands.items()))
        return bands

    def bandsAsNumPyList(self):
        band = self.bandNames()
        t = 1
        bands = []
        for i in band:
            bands.append(self.ds.GetRasterBand(t).ReadAsArray(0, 0, self.ds.RasterXSize, self.ds.RasterYSize))
            t += 1
        bands = np.array(bands)
        return bands
