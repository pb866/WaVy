#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""


"""

# Standard Packages
from tkinter import Tk, Frame, Menu, Toplevel, Label, IntVar, Button, \
     Radiobutton, Entry, PhotoImage, Text, Scrollbar, filedialog
import tkinter.messagebox as msg
import gdal
import numpy as np
import scipy as sp
import sys
# import to get version info
import tkinter
import spectral
# Plotting with TkInter
import matplotlib
# Specify MatPlotLib backend for use with tkinter
# This prevents crashes, when called from console or IPython
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

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
WaVy_version = "1.1-DEV"
# Author:      Steffen.Balmer / Florian.B. / Peter Bräuer
#
# Repository:  https://github.com/pb866/WaVy.git
# published under GNU general public license v3
#
# Created:     04.08.2016
# Copyright:   (c) Steffen.Balmer / Florian.B. 2016
# Last Modified: 06/2019 by Peter Bräuer
#                - Update to Python 3.7.3
#                - Beautifications
#                - Allow several spectral graphs in one plot with a legend of selected pixels
#                - Add license info to help menu
#                - Disable Image Menus, when no image file is selected
# -------------------------------------------------------------------------------
#
# TODO
# - Klassifikation mittel shapes und random forest/oder anderen Klassifikator
# - ndvi als envi file speichern
# - ndvi kanäle selbst wählen
# - pixel nummer kopieren
# - exception für int floatr eingaben bei SpectrumPlot
# -
# -------------------------------------------------------------------------------


class App(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()
        self.add_bindings()
        self.v = int
        self.xCoord = int
        self.yCoord = int

        self.redir = RedirectText(self.outputText)
        sys.stdout = self.redir
        sys.stderr = self.redir

    def initUI(self):
        self.parent.title("WaVy - Remote Sensing Software")

        self.menubar = Menu(self.parent)
        self.parent.config(menu=self.menubar)

        self.fileMenu = Menu(self.menubar, tearoff=False)
        self.fileMenu.add_command(label='Open File', command=self.openFile,
            accelerator='ctrl+o')
        self.fileMenu.add_command(label='Save Image As...', command=self.saveFig,
            accelerator='ctrl+s', state='disabled')
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label='Quit', command=self.onExit,
            accelerator='ctrl+q')
        self.menubar.add_cascade(label='File', menu=self.fileMenu)

        toolsMenu = Menu(self.menubar, tearoff=False)
        toolsMenu.add_command(label='Show Metadata', command=self.getMetaData,
            accelerator='ctrl+m')
        toolsMenu.add_command(label='Spectral Statstics', command=self.spectralStatistics,
            accelerator='ctrl+alt+s')
        toolsMenu.add_separator()
        toolsMenu.add_command(label='Plot Image', command=self.createImageWindow,
            accelerator='ctrl+i')
        toolsMenu.add_command(label='Plot Spectrum', command=self.createSpecWindow,
            accelerator='ctrl+p')
        self.menubar.add_cascade(label='Tools', menu=toolsMenu, state='disabled')

        imageMenu = Menu(self.menubar, tearoff=False)
        imageMenu.add_command(label='Show NDVI', command=self.showNDVI,
            accelerator='ctrl+n')
        imageMenu.add_command(label='Export NDVI', command=self.saveNDVI,
            accelerator='ctrl+e')
        self.menubar.add_cascade(label='Image', menu=imageMenu, state='disabled')

        vectorMenu = Menu(self.menubar, tearoff=False)
        vectorMenu.add_command(label='Load Cal', command='', accelerator='ctrl+alt+c')
        vectorMenu.add_command(label='Load Val', command='', accelerator='ctrl+alt+v')
        self.menubar.add_cascade(label='Vector', menu=vectorMenu, state='disabled')

        classifyMenu = Menu(self.menubar, tearoff=False)
        classifyMenu.add_command(label='n-K-Classifier', command='',
            accelerator='ctrl+c')
        self.menubar.add_cascade(label='Classification', menu=classifyMenu, state='disabled')

        helpMenu = Menu(self.menubar, tearoff=False)
        helpMenu.add_command(label='Used Packages', command=self.packagesVersions,
            accelerator='ctrl+alt+p')
        helpMenu.add_command(label='Contact Info', command=self.contact,
            accelerator='ctrl+alt+i')
        helpMenu.add_command(label='License', command=self.license,
            accelerator='ctrl+l')
        self.menubar.add_cascade(label='Help', menu=helpMenu)

        Frame1 = Frame(self.parent)
        self.photo = PhotoImage(file='WaVyLogo.png')
        self.label = Label(Frame1, image=self.photo)
        self.label.pack(padx=0, pady=0)
        Frame1.pack(side='top', fill='x', padx=0, pady=0)

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
                               text='WaVy – Version ' + WaVy_version +
                               '\nGitHub: https://github.com/pb866/WaVy.git',
                               justify='left', bd=1,
                               relief='sunken',
                               anchor='w', padx=10, pady=3)
        self.statusbar.pack(side='bottom', fill='x')
        Frame4.pack(fill='x', side='bottom')

    def add_bindings(self):
        # self.bind_all('<Key>', self.keyboard_shortcuts, add=False)
        self.bind_all('<Control-o>', self.keyboard_shortcuts, add=False)
        self.bind_all('<Control-s>', self.keyboard_shortcuts, add=False)
        self.bind_all('<Control-q>', self.keyboard_shortcuts, add=False)
        self.bind_all('<Control-m>', self.keyboard_shortcuts, add=False)
        self.bind_all('<Control-s>', self.keyboard_shortcuts, add=False)
        self.bind_all('<Control-i>', self.keyboard_shortcuts, add=False)
        self.bind_all('<Control-p>', self.keyboard_shortcuts, add=False)
        self.bind_all('<Control-n>', self.keyboard_shortcuts, add=False)
        self.bind_all('<Control-e>', self.keyboard_shortcuts, add=False)
        self.bind_all('<Control-Alt-c>', self.keyboard_shortcuts, add=False)
        self.bind_all('<Control-Alt-v>', self.keyboard_shortcuts, add=False)
        self.bind_all('<Control-c>', self.keyboard_shortcuts, add=False)
        self.bind_all('<Control-Alt-p>', self.keyboard_shortcuts, add=False)
        self.bind_all('<Control-Alt-i>', self.keyboard_shortcuts, add=False)
        self.bind_all('<Control-l>', self.keyboard_shortcuts, add=False)

    def openFile(self):
        dsObject = fil.NewFilePath()
        dsObject.openFile()
        self.parent.filePath = dsObject.getDs()
        if self.parent.filePath:
            self.enableMenu()
        else:
            self.disableMenu()

    def keyboard_shortcuts(self, event):
        if event.state==4 and event.keysym=='o':
            self.openFile()
        elif event.state==4 and event.keysym=='s':
            self.saveFig()
        elif event.state==4 and event.keysym=='q':
            self.onExit()
        elif event.state==4 and event.keysym=='m':
            self.getMetaData()
        elif event.state==20 and event.keysym=='s':
            self.spectralStatistics()
        elif event.state==4 and event.keysym=='i':
            self.createImageWindow()
        elif event.state==4 and event.keysym=='p':
            self.createSpecWindow()
        elif event.state==4 and event.keysym=='n':
            self.showNDVI()
        elif event.state==4 and event.keysym=='e':
            self.saveNDVI()
        elif event.state==20 and event.keysym=='c':
            pass
        elif event.state==20 and event.keysym=='v':
            pass
        elif event.state==4 and event.keysym=='c':
            pass
        elif event.state==20 and event.keysym=='p':
            self.packagesVersions()
        elif event.state==20 and event.keysym=='i':
            self.contact()
        elif event.state==4 and event.keysym=='l':
            self.license()


    def saveFig(self):
        fname = filedialog.asksaveasfilename(initialdir=".", title="Save Figure As...",
            filetypes=(("PDF", '*.pdf'), ("PS", '*.ps'), ("EPS", '*.eps'),
            ("PNG", '*.png'), ("JPEG", '*.jpg'), ("TIFF", '*.tif'),
            ('all file types', '*.*')))
        plt.savefig(fname)

    def getMetaData(self):
        try:
            dsObj = met.MetaData(self.parent.filePath)
            dsObj.showMeta()
        except (NameError, AttributeError):
            print('No ENVI Image File selected. Please, open a  file!')

    def spectralStatistics(self):
        try:
            specStatsObj = pltSta.StatisticsPlot(self.parent.filePath)
            specStatsObj.showStats()
            self.enableFig()
        except (NameError, AttributeError):
            print('No ENVI Image File selected. Please, open a  file!')

    def createImageWindow(self):
        try:
            self.optImagePlot = Toplevel(self)
            self.optImagePlot.title('Plot Image')
            self.optImagePlot.geometry("200x120+10+30")
        except (NameError, AttributeError):
            print('No ENVI Image File selected. Please, open a  file!')

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

        plotImageButton = Button(framePlot2, text='Plot Image',
            command=self.plotImageFunc).pack(side="left")
        coordsExitButton = Button(framePlot2, text='Exit',
            command=self.optImagePlot.destroy)
        coordsExitButton.pack(side="left")
        return self.v

    def plotImageFunc(self):
        try:
            plotObj = imgplt.PlotDataset(self.parent.filePath, self.v)
            plotObj.plotImage()
            self.enableFig()
        except (NameError, AttributeError):
            print('No ENVI Image File selected. Please, open a  file!')

    def createSpecWindow(self):
        try:
            self.coords = Toplevel(self)
            self.coords.title('Plot a spectrum')
            self.coords.geometry("300x110+10+30")
        except (NameError, AttributeError):
            print('No ENVI Image File selected. Please, open a  file!')

        frameCoords1 = Frame(self.coords, bd=2, relief="groove", padx=3, pady=3)
        frameCoords1.pack(side="top")
        frameCoords2 = Frame(self.coords)
        frameCoords2.pack(side="bottom")

        Label(frameCoords1, text='Pixel Coordinates?').grid(row=0, column=0)

        xCoordLabel = Label(frameCoords1, anchor="w", text='Zeile (Y-Koordinate):', width=20)
        xCoordLabel.grid(row=1, column=0)

        vcmd = (self.register(self.validate))
        self.xCoord = Entry(frameCoords1, validate='all', validatecommand=(vcmd, '%P'))
        self.xCoord.grid(row=1, column=1)

        yCoordLabel = Label(frameCoords1, anchor="w", text='Spalte (X-Koordinate):', width=20)
        yCoordLabel.grid(row=2, column=0)

        self.yCoord = Entry(frameCoords1, validate='all', validatecommand=(vcmd, '%P'))
        self.yCoord.grid(row=2, column=1)

        specObject = pltS.PlotSpectra(self.parent.filePath, self.xCoord, self.yCoord)
        coordsButton = Button(frameCoords2, text='Plot Spectrum',
            command=self.plotSpecFunc).grid(row=3, column=0)
        coordsButton = Button(frameCoords2, text='Clear Figure',
            command=specObject.clearFig).grid(row=3, column=1)
        coordsExitButton = Button(frameCoords2, text='Exit', command=self.coords.destroy)
        coordsExitButton.grid(row=3, column=2)

        return self.xCoord, self.yCoord

    def plotSpecFunc(self):
        try:
            specObject = pltS.PlotSpectra(self.parent.filePath, self.xCoord, self.yCoord)
            specObject.plotSpec()
            self.enableFig()
        except (NameError, AttributeError):
            print('No ENVI Image File selected. Please, open a  file!')
        except IndexError:
            self.meta = met.MetaData(self.parent.filePath)
            print("Out of bounds. Choose pixels in range y = 0...{1} and x = 0...{0}."
            .format(self.meta.ds.RasterXSize, self.meta.ds.RasterYSize))

    def showNDVI(self):
        try:
            ndviObj = vi.NDVI(self.parent.filePath)
            ndviObj.calcNDVI()
            self.enableFig()
        except (NameError, AttributeError):
            print('No ENVI Image File selected. Please, open a  file!')

    def saveNDVI(self):
        try:
            ndviSaveObj = viSave.SaveNDVI(self.parent.filePath)
            ndviSaveObj.writeNDVI()
            print('NDVI image saved!')
        except (NameError, AttributeError):
            print('No ENVI Image File selected. Please, open a  file!')

    def packagesVersions(self):
        msg.showinfo('Version Overview',
                     "Python version: {}\n\n"
                     "GDAL: version {}\nNumPy: version {}\nSciPy: version {}\n"
                     "TkInter: version {}\nSpectral: version {}\n"
                     "MatPlotLib: version {}"
                     .format(sys.version, gdal.VersionInfo(), np.__version__, sp.__version__,
                     tkinter.TkVersion, spectral.__version__, matplotlib.__version__))

    def validate(self, s):
        if s.isdigit():
            return True
        else:
            print('Please, enter integer digits only.')
            return False

    def contact(self):
        msg.showinfo('Contact', ('Kontaktinformationen\ns.b@future.com\n\n'
            'GitHub\nhttps://github.com/pb866/WaVy.git'))

    def license(self):
        msg.showinfo('License', str('This software is available under the\n' +
            'GNU General Public License v3.0\n\n' +
            'You can obtain a license copy at\n' +
            'https://www.gnu.org/licenses/gpl-3.0.html'))

    def enableMenu(self):
        self.menubar.entryconfig('Tools', state='normal')
        self.menubar.entryconfig('Image', state='normal')
        self.menubar.entryconfig('Vector', state='normal')
        self.menubar.entryconfig('Classification', state='normal')

    def disableMenu(self):
        self.menubar.entryconfig('Tools', state='disabled')
        self.menubar.entryconfig('Image', state='disabled')
        self.menubar.entryconfig('Vector', state='disabled')
        self.menubar.entryconfig('Classification', state='disabled')
        self.fileMenu.entryconfig('Save Image As...', state='disabled')

    def enableFig(self):
        self.fileMenu.entryconfig('Save Image As...', state='normal')

    def disableFig(self):
        pass

    def clearAll(self):
        self.outputText.delete('1.0', 'end')

    def onExit(self):
        #self.quit()
        self.parent.destroy()


class RedirectText:
    def __init__(self, text_ctrl):
        self.output = text_ctrl

    def write(self, string):
        self.output.update_idletasks()  # Update text windows, import to flush text before opening another window
        self.output.insert('current', string)

    def flush(self):
        pass


def main():
    root = Tk()
    app = App(root)
    app.mainloop()


if __name__ == '__main__':
    main()

    ##### um untermenus in der self.menubar zugenerieren
    # submenu = Menu(self.fileMenu)
    # submenu.add_command(label="New feed")
    # submenu.add_command(label="Bookmarks")
    # submenu.add_command(label="Mail")
    # self.fileMenu.add_cascade(label='Import', menu=submenu, underline=0)
