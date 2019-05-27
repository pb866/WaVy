#!/usr/bin/env python
from osgeo import gdal


class MetaData:
    def __init__(self, ds):
        self.ds = ds
    def showMeta(self):
        gt = self.ds.GetGeoTransform()
        geotransform = self.ds.GetGeoTransform()
        print(' Image Name: {} \n Image Size: {} x {} with {} bands \n Band Names: {} \n GSD: {} x {} m \n Image origin is X{} Y{} \n Image Projection: {}... \n Image Geo-Transform: {gt}'
        .format(self.ds.GetDescription(),
         self.ds.RasterYSize,
          self.ds.RasterXSize,
           self.ds.RasterCount,
            self.ds.GetMetadata(),
             geotransform[1],
              abs(geotransform[5]),
               geotransform[0],
                geotransform[3],
                 self.ds.GetProjection()[0:90],
                  gt=gt))
