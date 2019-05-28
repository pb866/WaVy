#!/usr/bin/env python
import gdal
import WaVyLib.imageConverter as converter


class SaveNDVI(converter.ConvertImage):
    def __init__(self, ds):
        super().__init__(self)
        self.ds = ds

    def writeNDVI(self):
        bands = self.bandsAsNumPy()
        ndvi = (bands['b5']-bands['b3'])/(bands['b5']+bands['b3'])
        driver = gdal.GetDriverByName('GTiff')
        fname = 'ndvi.tiff'
        rows, cols = ndvi.shape
        geo_transform = self.ds.GetGeoTransform()
        proj = self.ds.GetProjection()
        dataset = driver.Create(fname, cols, rows, 1, gdal.GDT_Float64)
        dataset.SetGeoTransform(geo_transform)
        dataset.SetProjection(proj)
        band = dataset.GetRasterBand(1)
        band.WriteArray(ndvi)
        dataset = None
        return 'NDVI saved!'
