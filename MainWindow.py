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
        self.clipButton=tk.Button(self.master,fg='blue',text='Save clips',command=self.funClip)
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
        self.picCanvas.bind('<Motion>',self.funCanvasMotion)
        self.picCanvas.pack(side=tk.TOP,expand=tk.YES,fill=tk.BOTH)
        self.cancelShow()
        if self.imageFiles:
            self.loadPicture(0)
        self.refreshTitle()
        # button engine status
        self.buttonStatus=0

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

    def refreshRectangles(self):
        # handles all added rectangles and if present the editee one also
        for qRectaPair in self.rectangles:
            if qRectaPair[1] is None:
                # must be added
                qRectaPair[0].sort()
                qRectaPair[1]=self.picCanvas.create_rectangle(qRectaPair[0].asTuple(),width=4,outline='red')
        # do we have an editee rectangle?
        if self.buttonStatus==1:
            # yes, we do
            if self.rectaID is not None:
                self.picCanvas.delete(self.rectaID)
            qRecta=SelRectangle(self.rectaCoordsStart,self.rectaCoordsEnd)
            qRecta.sort()
            self.rectaID=self.picCanvas.create_rectangle(qRecta.asTuple(),width=4,outline='blue')

    def funExit(self):
        self.master.quit()

    def funClip(self):
        for qInd,qRecta in enumerate(self.rectangles):
            if DEBUG:
                print 'Saving %i/%i ...' % (qInd+1,len(self.rectangles))
            print qRecta[0]
            print self.factor
            print qRecta[0].asTuple(1.0/self.factor)
            clippedImage=self.loadedImage.crop(qRecta[0].asTuple(1.0/self.factor))
            clippedImage.save('CLIP_%03i.jpg' % qInd,'jpeg')
        print 'Done.'

    def funCanvasClick(self,event,button):
        if DEBUG:
            print 'Clicker[%i]: %i,%i' % (button,event.x,event.y)
        if button==1:
            # left button
            if self.buttonStatus==0:
                # new rec starts
                self.rectaCoordsStart=(event.x,event.y)
                self.rectaCoordsEnd=self.rectaCoordsStart
                self.rectaID=None
                self.buttonStatus=1
            elif self.buttonStatus==1:
                # this is the second corner
                self.picCanvas.delete(self.rectaID)
                newRectangle=SelRectangle(self.rectaCoordsStart,(event.x,event.y))
                newRectangle.sort()
                self.rectangles.append([newRectangle,None])
                self.buttonStatus=0
        if button==3:
            # right button
            if self.buttonStatus==1:
                # abort current rectangle
                self.buttonStatus=0
        self.refreshRectangles()

    def funCanvasMotion(self,event):
        if DEBUG:
            print 'Motion: %i,%i' % (event.x,event.y)
        if self.buttonStatus==1:
            # adjust second corner
            self.rectaCoordsEnd=(event.x,event.y)
            self.refreshRectangles()