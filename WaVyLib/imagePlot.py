#!/usr/bin/env python
from spectral import *
import spectral.io.envi as envispec


class PlotDataset:
    def __init__(self, ds, v):
        self.ds = ds
        self.v = v

    def plotImage(self):
        name = self.ds.GetDescription()
        nameExt = name + '.hdr'
        img = envispec.open(nameExt, name)
        if self.v.get() == 1:
            return imshow(img, (2,1,0))
        elif self.v.get() == 2:
            return imshow(img, (4,2,1))