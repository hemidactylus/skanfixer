''' MainWindow: this class represents the main program window
    with its GUI elements.
'''

# standard imports
import Tkinter as tk
from PIL import Image, ImageTk
import os

# project imports
from SelRectangle import SelRectangle
from misc_utils import (isPicture,
                        findRescaleFactor,
                        listImageFiles,
                        centreAroundPoint,
                        mapCoordinatesFromZoom)

# edit modes
emINERT=0
emCREATING=1
# edit zoom overlay status
ezoNONE=0
ezoSHOWN=1

# TEMP - general settings
defaultSize=(640,480)
picZoomSize=(300,300)
picZoomFactor=3
# Debug flag
DEBUG=True

class MainWindow():

    def __init__(self,master,title=''):
        '''
            constructor requires a toplevel widget tk.Tk()
            which is the root main-window to which to attach the
            application.
        '''

        if DEBUG:
            print 'Init.'

        # Window layout
        self.master=master
        self.master.geometry('%dx%d' % defaultSize)
        # controls are in a frame
        self.controlPanel=tk.Frame(self.master)
        self.quitButton=tk.Button(self.controlPanel,text='Exit',command=self.funExit)
        self.quitButton.pack(side=tk.LEFT)
        self.clipButton=tk.Button(self.controlPanel,fg='blue',text='Save clips',command=self.funClip)
        self.clipButton.pack(side=tk.LEFT)

        self.browseButtons=[
                tk.Button(self.controlPanel,fg='green',text='-',command=lambda: self.funBrowse(0)),
                tk.Button(self.controlPanel,fg='green',text='+',command=lambda: self.funBrowse(1)),
            ]
        for qBBut in self.browseButtons:
            qBBut.pack(side=tk.LEFT)

        self.controlPanel.pack(side=tk.TOP)
        # canvas the image is shown in
        self.picCanvas=tk.Canvas(self.master,width=defaultSize[0],height=defaultSize[1])
        self.picCanvas.pack(side=tk.TOP,expand=tk.YES,fill=tk.BOTH)
        # function bindings
        self.picCanvas.bind('<Button-1>',lambda ev: self.funCanvasClick(ev,button=1))
        self.picCanvas.bind('<Button-2>',lambda ev: self.funCanvasClick(ev,button=2))
        self.picCanvas.bind('<Button-3>',lambda ev: self.funCanvasClick(ev,button=3))
        self.picCanvas.bind('<ButtonRelease-1>',lambda ev: self.funButtonRelease(ev,button=1))
        self.picCanvas.bind('<ButtonRelease-2>',lambda ev: self.funButtonRelease(ev,button=2))
        self.picCanvas.bind('<ButtonRelease-3>',lambda ev: self.funButtonRelease(ev,button=3))
        self.picCanvas.bind('<Motion>',self.funCanvasMotion)
        self.picCanvas.bind('<Configure>',self.funCanvasConfigure)

        # mouse position
        self.pointerPos=(None,None)

        # members setup, gui and appearance
        self.baseTitle=title
        self.canvasSize=defaultSize
        self.canvasImageHandle=None
        self.rectangles=[]
        # button engine status
        self.editMode=emINERT
        self.editZoomOverlay=ezoNONE
        self.zoomImage=None

        # reset dir/file info
        self.refreshFiles(None)
        # reset shown image
        self.cancelShow()
        # reset selections
        self.resetRectangles()

        # zoom overlay part
        self.picZoom=None

        if DEBUG:
            print self.imageFiles
        # show empty canvas in any case

        #self.rectaID=None
        self.newRectangle=None

        # auto-load first image, if any
        if self.imageFiles:
            self.loadPicture(0)
        else:
            self.refreshTitle()

    def funBrowse(self,direction):
        print 'Browse: %d.' % direction
        if self.imageFiles:
            self.resetRectangles()
            self.loadPicture((self.loadedImageIndex+[-1,+1][direction])%len(self.imageFiles))

    def resetRectangles(self):
        while self.rectangles:
            self.rectangles.pop().unshow(self.picCanvas)

    def refreshFiles(self,nDir):
        '''
            refresh current dir and reload list of images
        '''
        self.cwd=nDir if nDir is not None else os.getcwd()
        self.imageFiles=listImageFiles(self.cwd)

    def refreshTitle(self):
        curTitle=self.baseTitle
        # if self.cwd:
        #     if self.loadedImageIndex:
        #         self.imgName += ' - ' + os.path.join(self.cwd,self.imageFiles[self.loadedFileIndex])
        #     else:
        #         self.imgName += ' - ' + self.cwd
        if self.imgName:
            curTitle += ' - ' + self.imgName
        if self.loadedImage:
            curTitle += ' - ' + '[%i x %i]' % self.loadedImage.size
        self.master.title(curTitle)

    def cancelShow(self):
        if self.canvasImageHandle:
            self.picCanvas.delete_image(self.canvasImageHandle)
        self.canvasImageHandle=None
        self.loadedImage=None
        self.shownImage=None
        self.factor=None

    def loadPicture(self,imgIndex):
        '''
            argument must be an integer index in images list
        '''
        self.imgName=self.imageFiles[imgIndex]
        # open pic, find rescale factor
        if DEBUG:
            print 'Loading: %s' % self.imgName,
        self.loadedImageIndex=imgIndex
        self.loadedImage=Image.open(os.path.join(self.cwd,self.imageFiles[imgIndex]))
        self.refreshCanvas()
        self.refreshTitle()
        if DEBUG:
            print 'Done'

    def refreshRectangles(self):
        # handles all added rectangles and if present the editee one also
        for qRectaPair in self.rectangles:
            qRectaPair.unshow(self.picCanvas)
            qRectaPair.show(self.picCanvas,self.factor)

        # do we have an editee rectangle?
        if self.editMode==emCREATING:
            print 'SHOULD CHECK EZO'
            # Also check the not-quite-right rectangles positions
            # yes, we do
            if self.newRectangle:
                self.newRectangle.unshow(self.picCanvas)
            if self.newRectangle is not None:
                self.newRectangle.show(self.picCanvas,self.factor,color='blue')

    def funExit(self):
        self.master.quit()

    def funClip(self):
        for qInd,qRecta in enumerate(self.rectangles):
            if DEBUG:
                print 'Saving %i/%i ...' % (qInd+1,len(self.rectangles))
            print qRecta
            print self.factor
            clippedImage=self.loadedImage.crop(qRecta.asTuple(1.0))
            clippedImage.save('CLIP_%03i.jpg' % qInd,'jpeg')
        print 'Done.'

    def funButtonRelease(self,event,button):
        print 'RELEASE', button

    def funCanvasClick(self,event,button,zoom=False):
        ceventx,ceventy=event.x,event.y
        if zoom:
            ceventx,ceventy=mapCoordinatesFromZoom((event.x,event.y),self.zoomCenterPosition,
                picZoomSize, picZoomFactor)
            ceventx,ceventy=(x*self.factor for x in [ceventx,ceventy])
            # REFACTOR HERE THE WHOLE THING TO ALWAYS WORK IN PIC UNITS
            print 'ZoomClicker[%i]: %i,%i -> %i,%i' % (button,event.x,event.y,ceventx,ceventy)
        if DEBUG:
            print 'Clicker[%i]: %i,%i' % (button,ceventx,ceventy)
        if button==1:
            # left button
            if self.editMode==emINERT:
                # are we about to start moving a corner of a rectangle?
                recIndex,recCorner=self.findNearCorner(ceventx/self.factor,ceventy/self.factor)
                if recIndex is None:
                    # new rec starts
                    self.rectaCoordsStart=(ceventx/self.factor,ceventy/self.factor)
                    self.rectaCoordsEnd=self.rectaCoordsStart
                    self.newRectangle=SelRectangle(self.rectaCoordsStart,self.rectaCoordsEnd)
                    self.editMode=emCREATING
                    self.editZoomOverlay=ezoNONE
                else:
                    # enter editing of a rectangle
                    self.rectangles[recIndex].unshow(self.picCanvas)
                    delRecta=self.rectangles.pop(recIndex)
                    delRecta.unshow(self.picCanvas)
                    self.rectaCoordsStart=(delRecta.xs[1-recCorner[0]],delRecta.ys[1-recCorner[1]])
                    self.rectaCoordsEnd=(ceventx/self.factor,ceventy/self.factor)
                    self.newRectangle=SelRectangle(self.rectaCoordsStart,self.rectaCoordsEnd)
                    self.refreshRectangles()
                    self.editMode=emCREATING
                    self.editZoomOverlay=ezoSHOWN
                    self.createZoomOverlay()
            elif self.editMode==emCREATING:
                if self.editZoomOverlay==ezoSHOWN:
                    self.newRectangle.unshow(self.picZoom)
                    self.deleteZoomOverlay()
                # this is the second corner click: remove the edit rect and
                # add it to the rectangles' list
                self.newRectangle.sort()
                self.newRectangle.unshow(self.picCanvas)
                self.rectangles.append(self.newRectangle)
                self.newRectangle=None
                self.editMode=emINERT
                self.editZoomOverlay=ezoNONE
        if button==3:
            # right button
            if self.editMode==emCREATING:
                if self.editZoomOverlay==ezoSHOWN:
                    self.deleteZoomOverlay()
                # abort current rectangle creation
                self.editMode=emINERT
                self.editZoomOverlay=ezoNONE
                self.newRectangle.unshow(self.picCanvas)
                self.newRectangle=None
            else:
                # if pointer over an already created rectangle, delete it
                fndRecta=self.findNearRectangle(ceventx/self.factor,ceventy/self.factor)
                if fndRecta is not None:
                    self.rectangles[fndRecta].unshow(self.picCanvas)
                    self.removeRectangle(fndRecta)
        self.refreshRectangles()

    def findNearRectangle(self,cx,cy):
        TOL=15 # scaled pixels
        for qInd,qTuple in enumerate(self.rectangles):
            if qTuple.hasOnEdge(cx,cy,TOL/self.factor):
                return qInd
        return None

    def findNearCorner(self,cx,cy):
        # returns a 2uple index,corner - the last is a 2uple in (0,1)**2
        TOL=15 # scaled pixels
        for qInd,qTuple in enumerate(self.rectangles):
            qCorner=qTuple.hasOnCorner(cx,cy,TOL/self.factor)
            if qCorner is not None:
                return qInd,qCorner
        return None,None

    def removeRectangle(self,rectaIndex):
        self.rectangles[rectaIndex].unshow(self.picCanvas)
        self.rectangles.pop(rectaIndex)

    def funCanvasMotion(self,event,zoom=False):
        ceventx,ceventy=event.x,event.y
        if zoom:
            ceventx,ceventy=mapCoordinatesFromZoom((event.x,event.y),self.zoomCenterPosition,
                picZoomSize, picZoomFactor)
            # REFACTOR HERE
            ceventx,ceventy=(x*self.factor for x in [ceventx,ceventy])
            print 'ZoomMotion: %i,%i -> %i,%i' % (event.x,event.y,ceventx,ceventy)
        # if DEBUG:
        #     print 'Motion: %i,%i' % (event.x,event.y)
        self.pointerPos=(ceventx,ceventy)
        self.pointerImageSize=(ceventx/self.factor,ceventy/self.factor)
        if self.editMode==emCREATING:
            if self.editZoomOverlay==ezoSHOWN:
                if self.newRectangle:
                    self.newRectangle.unshow(self.picZoom)
            # adjust second corner
            self.rectaCoordsEnd=self.pointerImageSize
            self.newRectangle.unshow(self.picCanvas)
            self.newRectangle=SelRectangle(self.rectaCoordsStart,self.rectaCoordsEnd)
            self.newRectangle.show(self.picCanvas,self.factor,color='blue')
            if self.editZoomOverlay==ezoSHOWN:
                if self.newRectangle:
                    self.newRectangle.show(self.picZoom,picZoomFactor,width=2,color='blue',offset=self.clipRegionStart)

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
            self.refreshRectangles()

    def createZoomOverlay(self):
        '''
            Creates the zoom patch around the mouse cursor
        '''
        print 'CREATE ZOOM OVERLAY'
        self.deleteZoomOverlay()
        self.picZoom=tk.Canvas(self.picCanvas,width=picZoomSize[0],height=picZoomSize[1])
        # bind events to zoom frame
        self.picZoom.bind('<Button-1>',lambda ev: self.funCanvasClick(ev,button=1,zoom=True))
        self.picZoom.bind('<Button-2>',lambda ev: self.funCanvasClick(ev,button=2,zoom=True))
        self.picZoom.bind('<Button-3>',lambda ev: self.funCanvasClick(ev,button=3,zoom=True))
        self.picZoom.bind('<Motion>',lambda ev: self.funCanvasMotion(ev,zoom=True))
        #
        cornX,cornY=centreAroundPoint(self.pointerPos,picZoomSize)
        # store position of zoom window
        self.zoomCenterPosition=self.pointerImageSize
        # perform zoom
        self.clipRegionStart=centreAroundPoint(self.pointerImageSize,
            (zoCoo/picZoomFactor for zoCoo in picZoomSize))
        self.clipRegionEnd=(coo+(clipSize/picZoomFactor) for coo,clipSize in zip(self.clipRegionStart,picZoomSize))
        clipCoords=[int(coo) for qlist in [self.clipRegionStart,self.clipRegionEnd] for coo in qlist]
        print clipCoords
        self.zoomImage=ImageTk.PhotoImage(self.loadedImage.crop(clipCoords).resize(picZoomSize,Image.NEAREST))
        self.picZoom.create_image(0,0,anchor=tk.NW,image=self.zoomImage)
        self.picZoom.place(x=cornX,y=cornY)
        # handle recta's on zoom overlay. Calculate offset for invoking rectas' show()
        # the offset is in real-pic units
        for qrecta in self.rectangles:
            qrecta.show(self.picZoom,picZoomFactor,width=2,color='red',offset=self.clipRegionStart)
        if self.newRectangle:
            self.newRectangle.show(self.picZoom,picZoomFactor,width=2,color='blue',offset=self.clipRegionStart)

    def deleteZoomOverlay(self):
        if self.picZoom is not None:
            for qrecta in self.rectangles:
                qrecta.unshow(self.picZoom)
            self.picZoom.destroy()
