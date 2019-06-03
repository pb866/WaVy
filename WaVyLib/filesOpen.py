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
        success = False
        while not success:
            try:
                self.ds = self.getFilePath()
                self.fname = os.path.basename(self.ds.GetDescription())
                print('The image {} was loaded successfully'.format(self.fname))
                success = True
            except:
                # again=input("Image doesn't exist or is corrupted. Try again (y)?")
                # if again.lower()[0] != 'y': success = True
                print("Image doesn't exist or is corrupted. Try again!")

    def getDs(self):
        return self.ds
