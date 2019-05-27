#!/usr/bin/env python
from osgeo import gdal
from tkinter.filedialog import askopenfilename


class NewFilePath:
    def getFilePath(self):
        driver = gdal.GetDriverByName('ENVI')
        driver.Register()
        return gdal.Open(askopenfilename())

    def openFile(self):
         self.ds = self.getFilePath()
         print('The image {} is loaded successfully'.format(self.ds.GetDescription()))

    def getDs(self):
        return self.ds
