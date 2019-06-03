#!/usr/bin/env python
import gdal
from tkinter.filedialog import askopenfilename
import os.path


class NewFilePath:
    def getFilePath(self):
        driver = gdal.GetDriverByName('ENVI')
        driver.Register()
        return gdal.Open(askopenfilename())

    def openFile(self):
         self.ds = self.getFilePath()
         self.fname = os.path.basename(self.ds.GetDescription())
         print('The image {} was loaded successfully'.format(self.fname))

    def getDs(self):
        return self.ds
