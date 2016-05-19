''' MainWindow: this class represents the main program window
    with its GUI elements.
'''

defaultSize=(640,480)

DEBUG=True

import Tkinter as tk
from PIL import Image, ImageTk
import os

from SelRectangle import SelRectangle

def isPicture(filename):
    return filename[-3:].lower() == 'jpg' or filename[-4:].lower() == 'jpeg'

def findRescaleFactor(imgSize,allowedSize):
    mFactor=min(float(alwDim)/float(imgDim) for imgDim,alwDim in zip(imgSize,allowedSize))
    # if mFactor>1:
    #     mFactor=1
    if DEBUG:
        print 'mFactor=%.3f' % mFactor
    return mFactor

class MainWindow():

    def __init__(self,master,title):
        self.master=master

        self.controlPanel=tk.Frame(self.master)
        self.quitButton=tk.Button(self.controlPanel,text='Exit',command=self.funExit)
        self.quitButton.pack(side=tk.LEFT)
        self.clipButton=tk.Button(self.controlPanel,fg='blue',text='Save clips',command=self.funClip)
        self.clipButton.pack(side=tk.LEFT)
        self.master.geometry('%dx%d' % defaultSize)
        self.controlPanel.pack(side=tk.TOP)
        self.rectangles=[]
        self.baseTitle=title
        # handle pictures to load
        self.cwd=os.getcwd()
        self.refreshFiles(self.cwd)
        if DEBUG:
            print self.imageFiles
        # show empty canvas in any case
        self.canvasSize=defaultSize
        self.picCanvas=tk.Canvas(self.master,width=defaultSize[0],height=defaultSize[1])
        self.canvasImageHandle=None
        self.rectaID=None
        self.newRectangle=None
        print 'THESE TWO MUST FORM A PAIR'
        self.picCanvas.bind('<Button-1>',lambda ev: self.funCanvasClick(ev,button=1))
        self.picCanvas.bind('<Button-2>',lambda ev: self.funCanvasClick(ev,button=2))
        self.picCanvas.bind('<Button-3>',lambda ev: self.funCanvasClick(ev,button=3))
        self.picCanvas.bind('<Motion>',self.funCanvasMotion)
        self.picCanvas.bind('<Configure>',self.funCanvasConfigure)
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
        self.refreshCanvas()

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
                qRectaPair[1]=self.picCanvas.create_rectangle(qRectaPair[0].asTuple(self.factor),width=4,outline='red')
        # do we have an editee rectangle?
        if self.buttonStatus==1: # this must become more seriously handled. Not a clicked button!
            # Also check the not-quite-right rectangles positions
            # yes, we do
            if self.rectaID is not None:
                self.picCanvas.delete(self.rectaID)
            if self.newRectangle is not None:
                self.rectaID=self.picCanvas.create_rectangle(self.newRectangle.asTuple(self.factor),width=4,outline='blue')

    def funExit(self):
        self.master.quit()

    def funClip(self):
        for qInd,qRecta in enumerate(self.rectangles):
            if DEBUG:
                print 'Saving %i/%i ...' % (qInd+1,len(self.rectangles))
            print qRecta[0]
            print self.factor
            clippedImage=self.loadedImage.crop(qRecta[0].asTuple(1.0))
            clippedImage.save('CLIP_%03i.jpg' % qInd,'jpeg')
        print 'Done.'

    def funCanvasClick(self,event,button):
        if DEBUG:
            print 'Clicker[%i]: %i,%i' % (button,event.x,event.y)
        if button==1:
            # left button
            if self.buttonStatus==0:
                # new rec starts
                self.rectaCoordsStart=(event.x/self.factor,event.y/self.factor)
                self.rectaCoordsEnd=self.rectaCoordsStart
                self.newRectangle=SelRectangle(self.rectaCoordsStart,self.rectaCoordsEnd)
                self.rectaID=None
                self.buttonStatus=1
            elif self.buttonStatus==1:
                # this is the second corner
                self.picCanvas.delete(self.rectaID)
                self.newRectangle.sort()
                self.rectangles.append([self.newRectangle,None])
                self.newRectangle=None
                self.buttonStatus=0
        if button==3:
            # right button
            if self.buttonStatus==1:
                # abort current rectangle creation
                self.buttonStatus=0
                if self.rectaID is not None:
                    self.picCanvas.delete(self.rectaID)
            else:
                # if pointer over an already created rectangle, delete it
                fndRecta=self.findNearRectangle(event.x/self.factor,event.y/self.factor)
                #fndRecta=0
                print 'HERE SHOULD FIND RECTA'
                if fndRecta is not None:
                    self.removeRectangle(fndRecta)
        self.refreshRectangles()

    def findNearRectangle(self,cx,cy):
        TOL=15 # scaled pixels
        for qInd,qTuple in enumerate(self.rectangles):
            if qTuple[0].hasOnEdge(cx,cy,TOL):
                return qInd
        return None

    def removeRectangle(self,rectaIndex):
        self.picCanvas.delete(self.rectangles[rectaIndex][1])
        self.rectangles.pop(rectaIndex)

    def funCanvasMotion(self,event):
        if DEBUG:
            print 'Motion: %i,%i' % (event.x,event.y)
        if self.buttonStatus==1:
            # adjust second corner
            self.rectaCoordsEnd=(event.x/self.factor,event.y/self.factor)
            self.newRectangle=SelRectangle(self.rectaCoordsStart,self.rectaCoordsEnd)
            self.refreshRectangles()

    def funCanvasConfigure(self,event):
        # resize of window, hence of canvas
        self.canvasSize=(event.width,event.height)
        if DEBUG:
            print 'CONFIG!'
        self.refreshCanvas()

    def refreshCanvas(self):
        # redraw, resize, etc
        if self.loadedImage:
            self.factor=findRescaleFactor(self.loadedImage.size,self.canvasSize)
            # create the scaled (shown) image
            shownSize=tuple(int(ldDim * self.factor) for ldDim in self.loadedImage.size)
            if DEBUG:
                print 'shownSize:', shownSize
            self.shownImage=self.loadedImage.resize(shownSize, Image.ANTIALIAS)
            # make the tour through PIL to show image and so on
            self.tkShownImage=ImageTk.PhotoImage(self.shownImage)
            self.canvasImageHandle=self.picCanvas.create_image(0,0,anchor=tk.NW,image=self.tkShownImage)
            # must redraw all rectangles as well
            for qRectaPair in self.rectangles:
                if qRectaPair[1] is not None:
                    self.picCanvas.delete(qRectaPair[1])
                    qRectaPair[1]=self.picCanvas.create_rectangle(qRectaPair[0].asTuple(self.factor),width=4,outline='red')
            if self.rectaID is not None:
                self.picCanvas.delete(self.rectaID)
            if self.newRectangle is not None:
                # these lines duplicate refresh rectangles above!
                self.rectaID=self.picCanvas.create_rectangle(self.newRectangle.asTuple(self.factor),width=4,outline='blue')
