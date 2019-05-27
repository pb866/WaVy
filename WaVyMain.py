#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""


"""

# Standard Packages
from tkinter import Tk, Frame, Menu, Toplevel, Label, IntVar, Button, Radiobutton, Entry, PhotoImage, Text, Scrollbar
import tkinter.messagebox as msg
from osgeo import gdal
import numpy as np
import scipy as sp
import sys

# Local Packages
import WaVyLib.filesOpen as fil
import WaVyLib.dataMeta as met
import WaVyLib.plotStatistcs as pltSta
import WaVyLib.imagePlot as imgplt
import WaVyLib.spectraPlot as pltS
import WaVyLib.ndviCalc as vi
import WaVyLib.ndviSave as viSave

# -------------------------------------------------------------------------------
# Name:        WaVy
WaVy_version = str(1.0)
# Author:      Steffen.Balmer / Florian.B.
#
# Created:     04.08.2016
# Copyright:   (c) Steffen.Balmer / Florian.B. 2016
# -------------------------------------------------------------------------------
#
# TODO
# - Klassifikation mittel shapes und random forest/oder anderen Klassifikator
# - ndvi als envi file speichern
# - ndvi kanäle selbst wählen
# - pixel nummer kopieren
# - packagefenster verbessern
# - exception für int floatr eingaben bei SpectrumPlot
# -
# -------------------------------------------------------------------------------


class App(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()
        self.v = int
        self.xCoord = int
        self.yCoord = int

        self.redir = RedirectText(self.outputText)
        sys.stdout = self.redir

    def initUI(self):
        self.parent.title("WaVy - Remote Sensing Software")

        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)

        fileMenu = Menu(menubar, tearoff=False)
        fileMenu.add_command(label='Open File', command=self.openFile)
        fileMenu.add_separator()
        fileMenu.add_command(label='Exit', command=self.onExit)
        menubar.add_cascade(label='File', menu=fileMenu)

        toolsMenu = Menu(menubar, tearoff=False)
        toolsMenu.add_command(label='Show Metadata', command=self.getMetaData)
        toolsMenu.add_command(label='Spectral Statstics', command=self.spectralStatistics)
        toolsMenu.add_separator()
        toolsMenu.add_command(label='Plot Image', command=self.createImageWindow)
        toolsMenu.add_command(label='Plot Spectrum', command=self.createSpecWindow)
        menubar.add_cascade(label='Tools', menu=toolsMenu)

        imageMenu = Menu(menubar, tearoff=False)
        imageMenu.add_command(label='Show NDVI', command=self.showNDVI)
        imageMenu.add_command(label='Save NDVI', command=self.saveNDVI)
        menubar.add_cascade(label='Image', menu=imageMenu)

        vectorMenu = Menu(menubar, tearoff=False)
        vectorMenu.add_command(label='Load Cal', command='')
        vectorMenu.add_command(label='Load Val', command='')
        menubar.add_cascade(label='Vector', menu=vectorMenu)

        classifyMenu = Menu(menubar, tearoff=False)
        classifyMenu.add_command(label='n-K-Classifier', command='')
        menubar.add_cascade(label='Classification', menu=classifyMenu)

        helpMenu = Menu(menubar, tearoff=False)
        helpMenu.add_command(label='Used Packages', command=self.packagesVersions)
        helpMenu.add_command(label='Contact', command=self.contact)
        menubar.add_cascade(label='Help', menu=helpMenu)

        Frame1 = Frame(self.parent)
        self.photo = PhotoImage(file='logo.png')
        self.label = Label(Frame1, image=self.photo)
        self.label.pack()
        Frame1.pack(side='top', fill='x')

        Frame2 = Frame(self.parent)
        self.outputText = Text(Frame2, width=50, height=20, wrap="word", )
        self.scrollbar = Scrollbar(Frame2)
        self.scrollbar.config(command=self.outputText.yview)
        self.outputText.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='both', expand=False)
        self.outputText.pack(side='top', fill='both', expand=True)
        Frame2.pack(fill='both')

        Frame3 = Frame(self.parent)
        self.clearButton = Button(Frame3, text='Clear Window', command=self.clearAll)
        self.clearButton.pack(anchor='e')
        Frame3.pack(fill='x')

        Frame4 = Frame(self.parent)
        self.statusbar = Label(Frame4,
                               text='Kontaktinfos, WaVy Version: ' + WaVy_version,
                               bd=1,
                               relief='sunken',
                               anchor='w')
        self.statusbar.pack(side='bottom', fill='x')
        Frame4.pack(fill='x', side='bottom')

    def openFile(self):
        try:
            dsObject = fil.NewFilePath()
            dsObject.openFile()
            self.parent.filePath = dsObject.getDs()
        except (AttributeError, FileExistsError, FileNotFoundError, ImportError, ValueError) as e:
            print('ERROR: No ENVI Image File selected!\n\nError description: ', e.args[0], '\n\nPLEASE, try again!')

    def getMetaData(self):
        try:
            dsObj = met.MetaData(self.parent.filePath)
            dsObj.showMeta()
        except (NameError, AttributeError) as err:
            print('No ENVI Image File selected!\n\nError description: ', err.args[0], '\n\nPLEASE, open a  file!')

    def spectralStatistics(self):
        try:
            specStatsObj = pltSta.StatisticsPlot(self.parent.filePath)
            specStatsObj.showStats()
        except (NameError, AttributeError) as err:
            print('No ENVI Image File selected!\n\nError description: ', err.args[0], '\n\nPLEASE, open a  file!')

    def createImageWindow(self):
        try:
            self.optImagePlot = Toplevel(self)
            self.optImagePlot.title('Plot Image')
            self.optImagePlot.geometry("200x120+10+30")
        except (NameError, AttributeError) as err:
            print('No ENVI Image File selected!\n\nError description: ', err.args[0], '\n\nPLEASE, open a  file!')

        framePlot1 = Frame(self.optImagePlot, bd=2, relief="groove", padx=3, pady=3)
        framePlot1.pack(side="top")
        framePlot2 = Frame(self.optImagePlot)
        framePlot2.pack(side="bottom")

        Label(framePlot1, text='RGB oder VNIR?').pack()

        self.v = IntVar()
        rgbOpt = Radiobutton(framePlot1, text="Red/Green/Blue", variable=self.v, value=1)
        rgbOpt.pack()
        vnirOpt = Radiobutton(framePlot1, text="NIR/Red/Green", variable=self.v, value=2)
        vnirOpt.pack()

        plotImageButton = Button(framePlot2, text='Plot Image', command=self.plotImageFunc).pack(side="left")
        coordsExitButton = Button(framePlot2, text='Exit', command=self.optImagePlot.destroy)
        coordsExitButton.pack(side="left")
        return self.v

    def plotImageFunc(self):
        try:
            plotObj = imgplt.PlotDataset(self.parent.filePath, self.v)
            plotObj.plotImage()
        except (NameError, AttributeError) as err:
            print('No ENVI Image File selected!\n\nError description: ', err.args[0], '\n\nPLEASE, open a  file!')

    def createSpecWindow(self):
        try:
            self.coords = Toplevel(self)
            self.coords.title('Plot a spectrum')
            self.coords.geometry("300x110+10+30")
        except (NameError, AttributeError) as err:
            print('No ENVI Image File selected!\n\nError description: ', err.args[0], '\n\nPLEASE, open a  file!')

        frameCoords1 = Frame(self.coords, bd=2, relief="groove", padx=3, pady=3)
        frameCoords1.pack(side="top")
        frameCoords2 = Frame(self.coords)
        frameCoords2.pack(side="bottom")

        Label(frameCoords1, text='Pixel Coordinates?').grid(row=0, columnspan=2)

        xCoordLabel = Label(frameCoords1, anchor="w", text='Zeile (Y-Koordinate):', width=20)
        xCoordLabel.grid(row=1, column=0)

        self.xCoord = Entry(frameCoords1)
        self.xCoord.grid(row=1, column=1)

        yCoordLabel = Label(frameCoords1, anchor="w", text='Spalte (X-Koordinate):', width=20)
        yCoordLabel.grid(row=2, column=0)

        self.yCoord = Entry(frameCoords1)
        self.yCoord.grid(row=2, column=1)

        coordsButton = Button(frameCoords2, text='Plot Spectrum', command=self.plotSpecFunc).grid(row=3, column=0)
        coordsExitButton = Button(frameCoords2, text='Exit', command=self.coords.destroy)
        coordsExitButton.grid(row=3, column=1)

        return self.xCoord, self.yCoord

    def plotSpecFunc(self):
        try:
            specObject = pltS.PlotSpectra(self.parent.filePath, self.xCoord, self.yCoord)
            specObject.plotSpec()
        except (NameError, AttributeError) as err:
            print('No ENVI Image File selected!\n\nError description: ', err.args[0], '\n\nPLEASE, open a  file!')

    def showNDVI(self):
        try:
            ndviObj = vi.NDVI(self.parent.filePath)
            ndviObj.calcNDVI()
        except (NameError, AttributeError) as err:
            print('No ENVI Image File selected!\n\nError description: ', err.args[0], '\n\nPLEASE, open a  file!')

    def saveNDVI(self):
        try:
            ndviSaveObj = viSave.SaveNDVI(self.parent.filePath)
            ndviSaveObj.writeNDVI()
            print('NDVI image saved!')
        except (NameError, AttributeError) as err:
            print('No ENVI Image File selected!\n\nError description: ', err.args[0], '\n\nPLEASE, open a  file!')

    def packagesVersions(self):
        msg.showinfo('Important Packages:',
                     "GDAL's version is: {} \n {} \n NumPy's version is: {} \n {} \n SciPy's version is: {} \n {}"
                     .format(gdal.__version__, gdal, np.__version__, np, sp.__version__, sp))

    def contact(self):
        msg.showinfo('Contact', 'Kontaktinformationen\ns.b@future.com')

    def clearAll(self):
        self.outputText.delete('1.0', 'end')

    def onExit(self):
        #self.quit()
        self.parent.destroy()


class RedirectText:
    def __init__(self, text_ctrl):
        self.output = text_ctrl

    def write(self, string):
        self.output.insert('end', string)

    def flush(self):
        pass


def main():
    root = Tk()
    app = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()

    ##### um untermenus in der Menubar zugenerieren
    # submenu = Menu(fileMenu)
    # submenu.add_command(label="New feed")
    # submenu.add_command(label="Bookmarks")
    # submenu.add_command(label="Mail")
    # fileMenu.add_cascade(label='Import', menu=submenu, underline=0)