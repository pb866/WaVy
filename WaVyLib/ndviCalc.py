#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import WaVyLib.imageConverter as converter


class NDVI(converter.ConvertImage):
    def __init__(self, ds):
        super().__init__(self)
        self.ds = ds

    def calcNDVI(self):
        bands = self.bandsAsNumPy()
        ndvi = (bands['b5']-bands['b3'])/(bands['b5']+bands['b3'])
        print('NDVI-Statistik:  Min = {:.2f}, Max = {:.2f}, Mean = {:.2f}, Std = {:.2f}'.format(np.min(ndvi), np.max(ndvi), np.mean(ndvi), np.std(ndvi)))
        plt.clf()
        ndviIMG=plt.imshow(ndvi, interpolation='nearest', cmap='RdYlGn', clim=(0.0, 1.0))
        plt.colorbar()
        plt.show()
