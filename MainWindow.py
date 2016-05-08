''' MainWindow: this class represents the main program window
    with its GUI elements.
'''

defaultSize=(640,480)
maxWindowSize=(1000,600)
deltaSize=(0,65)

DEBUG=True

import Tkinter as tk
from PIL import Image, ImageTk
import os

from SelRectangle import SelRectangle

def isPicture(filename):
    return filename[-3:].lower() == 'jpg' or filename[-4:].lower() == 'jpeg'

def findRescaleFactor(imgSize,allowedSize):
    mFactor=min(float(alwDim)/float(imgDim) for imgDim,alwDim in zip(imgSize,allowedSize))
    if mFactor>1:
        mFactor=1
    if DEBUG:
        print 'mFactor=%.3f' % mFactor
    return mFactor

class MainWindow():

    def __init__(self,master,title):
        self.master=master
        self.quitButton=tk.Button(self.master,text='Exit',command=self.funExit)
        self.quitButton.pack(side=tk.TOP)
        self.clipButton=tk.Button(self.master,fg='blue',text='Click',command=self.funClip)
        self.clipButton.pack(side=tk.TOP)
        self.master.geometry('%dx%d' % defaultSize)
        self.rectangles=[]
        self.baseTitle=title
        # handle pictures to load
        self.cwd=os.getcwd()
        self.refreshFiles(self.cwd)
        if DEBUG:
            print self.imageFiles
        # show empty canvas in any case
        self.picCanvas=tk.Canvas(self.master,width=defaultSize[0],height=defaultSize[1])
        self.canvasImageHandle=None
        self.picCanvas.bind('<Button-1>',lambda ev: self.funCanvasClick(ev,button=1))
        self.picCanvas.bind('<Button-2>',lambda ev: self.funCanvasClick(ev,button=2))
        self.picCanvas.bind('<Button-3>',lambda ev: self.funCanvasClick(ev,button=3))
        self.picCanvas.pack(side=tk.TOP,expand=tk.YES,fill=tk.BOTH)
        self.cancelShow()
        if self.imageFiles:
            self.loadPicture(1)
        self.refreshTitle()

    def refreshTitle(self):
        curTitle=self.baseTitle
        if self.loadedFileName:
            curTitle += ' - ' + self.loadedFileName
        if self.loadedImage:
            curTitle += ' [%i x %i]' % self.loadedImage.size
        self.master.title(curTitle)

    def cancelShow(self):
        if self.canvasImageHandle:
            self.picCanvas.delete_image(self.canvasImageHandle)
        self.canvasImageHandle=None
        self.loadedImage=None
        self.shownImage=None
        self.factor=None

    def loadPicture(self,imgArg):
        '''
            argument can be either a filename (string) or an index in images list
        '''
        if isinstance(imgArg,int):
            imgArg=self.imageFiles[imgArg]
        # open pic, find rescale factor
        self.loadedFileName=imgArg
        self.loadedImage=Image.open(os.path.join(self.cwd,imgArg))
        self.factor=findRescaleFactor(self.loadedImage.size,maxWindowSize)
        # create the scaled (shown) image
        shownSize=tuple(int(ldDim * self.factor) for ldDim in self.loadedImage.size)
        if DEBUG:
            print 'shownSize:', shownSize
        resizeSize=tuple(pDim+pDelta for pDim,pDelta in zip(shownSize,deltaSize))
        self.master.geometry('%dx%d' % resizeSize)
        self.shownImage=self.loadedImage.resize(shownSize, Image.ANTIALIAS)
        # make the tour through PIL to show image and so on
        self.tkShownImage=ImageTk.PhotoImage(self.shownImage)
        self.canvasImageHandle=self.picCanvas.create_image(0,0,anchor=tk.NW,image=self.tkShownImage)


    def refreshFiles(self,nDir):
        '''
            refresh current dir and reload list of images
        '''
        self.dir=nDir
        self.imageFiles=[fN for fN in os.listdir(nDir) if isPicture(fN)]

    def refreshRecta(self):
        if any([x is None for x in self.recta]):
            print 'Abo', self.recta
            if self.recid is not None:
                self.picCanvas.delete(self.recid)
            self.recid=None
            return
        else:
            if self.recid is not None:
                self.picCanvas.delete(self.recid)
            self.recid=self.picCanvas.create_rectangle(tuple(coo*self.factor for coo in self.recta),width=4,outline='red')
            print 'Rekta', self.recta

    def funExit(self):
        self.master.quit()
    def funClip(self):
        if len(self.rectangles)>0:
            print 'Saving... ',
            nimg=self.image1.crop(self.recta)
            nimg.save('CLIP.jpg','jpeg')
            print 'Done.'
        else:
            if DEBUG:
                print 'No rectangles'

    def funCanvasClick(self,event,button):
        print 'Clicker[%i]: %i,%i' % (button,event.x,event.y)
        self.recta[0]=int(event.x/self.factor)
        self.recta[1]=int(event.y/self.factor)
        self.refreshRecta()
        # print 'ClickerR: %i,%i' % (event.x,event.y)
        # self.recta[2]=int(event.x/self.factor)
        # self.recta[3]=int(event.y/self.factor)
        # self.refreshRecta()
