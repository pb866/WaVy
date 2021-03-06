#!/usr/bin/env python
import numpy as np
import collections
import matplotlib.pyplot as plt
import WaVyLib.imageConverter as converter


class StatisticsPlot(converter.ConvertImage):
    def __init__(self, ds):
        super().__init__(self)
        self.ds = ds

    def showStats(self):
        band = self.bandNames() # get band names
        bands = self.bandsAsNumPy() # get bands as numpy arrays
        t = 1
        # bands in a dictionary
        bandsStats = {}
        for i in bands:
             bandsStats[band[t-1]] = self.ds.GetRasterBand(t).GetStatistics(True,True)
             t += 1
        # the dictionary isn't ordered, thus we have to order is by band names
        bandsStats = collections.OrderedDict(sorted(bandsStats.items()))

        print(bandsStats,
              'Minimum/Maximum/Mean/Standard deviation per band: \n',
              "The ANOVA statistics for each band are: \n")

        # Mean in one List
        bandsStatsMean = []
        for b in bandsStats:
            bandsStatsMean.append(bandsStats[b][2])
        bandsStatsMean = np.array(bandsStatsMean)

        # # Standard deviation in one List
        bandsStatsStd = []
        for b in bandsStats:
            bandsStatsStd.append(bandsStats[b][3])
        bandsStatsStd = np.array(bandsStatsStd)

        plt.clf()
        plt.plot(bandsStatsMean, ls = '--', label ='Mean')
        plt.plot(bandsStatsMean+bandsStatsStd/2, ls = ':', label = '+ Std')
        plt.plot(bandsStatsMean-bandsStatsStd/2, ls = ':', label = '- Std')
        plt.xticks(range(len(band)), band)
        plt.xlabel("bands")
        plt.grid(ls=':')
        plt.legend()
        plt.show(block=False)
