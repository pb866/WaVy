#!/usr/bin/env python
# import numpy as np
import matplotlib.pyplot as plt
import WaVyLib.imageConverter as converter


class PlotSpectra(converter.ConvertImage):
    def __init__(self, ds, xCoord, yCoord):
        super().__init__(self)
        self.ds = ds
        self.xCoord = xCoord
        self.yCoord = yCoord

    def plotSpec(self):
        band = self.bandNames() # get band names
        bands = self.bandsAsNumPyList()
        coordX = int(self.xCoord.get())
        coordY = int(self.yCoord.get())
        plt.plot(bands[:, coordX, coordY])
        plt.xticks(range(len(band)), band)
        plt.grid(ls=":")
        plt.title("Bands at x = {}, y = {}".format(coordX, coordY))
        plt.show()
