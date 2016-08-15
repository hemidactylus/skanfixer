#!/usr/bin/env python

""" Skanfixer, semi-automatic handling of extracting photos from scanned
    pages. Author: hemidactylus
"""

# edit modes
emINERT=0
emEDITCORNER=1
emEDITSIDE=2

# standard imports
import Tkinter as tk
from PIL import Image, ImageTk
import os
import math
from time import time

# skanfixer imports
from sfPoint import sfPoint
from sfRectangle import sfRectangle
from sfCanvas import sfCanvas
from sfAffineMaps import createAffineMap
from sfSettings import settings
from sfUtilities import (
                            popItem,
                            listImageFiles,
                            findRescaleFactor,
                        )

class sfMain():

    def __init__(self,master):
        '''
            The object 'testWindow' has various families of data members:

                <file/image info: a list of img files, whether/which is loaded, a dir name>
                <visualisation info: zoom factor and so on>
                <edit status, presence of zoom, etc>

                * edit:                     presence of zoom, mouse position, etc
                    - edit.cursorPos:       a (image-coordinate) sfPoint
                    - edit.status:          edit mode (shaping a recta/not)
                    - edit.targetRectangle: if shaping a recta, this is a sfRectangle
                    - edit.targetPoint:     if shaping a recta, this is the grabbed corner/side index

                * rectangles:               a list of rectangles (with their bindings and everything)
        '''

        # handy miniclasses for datamembers
        class sfEditStatus():
            cursorPos=sfPoint()
            status=emINERT
            targetRectangle=None
            targetPoint=0
            undoRectangle=None
            buttonPressed=None
            buttonTime=None

        # setting up the data members
        self.rectangles=[]
        self.edit=sfEditStatus()

        print 'Init.'

        # Window layout
        self.master=master
        self.master.geometry('%ix%i' % (settings['WINDOW_SIZE']['WIDTH'],settings['WINDOW_SIZE']['HEIGHT']))
        # controls are in a frame
        self.controlPanel=tk.Frame(self.master)
        self.quitButton=tk.Button(self.controlPanel,text='Exit',command=self.funExit)
        self.quitButton.pack(side=tk.LEFT)
        self.shiftButtons=[
            tk.Button(self.controlPanel,text='<<',command=lambda: self.funBrowse(delta=-1)),
            tk.Button(self.controlPanel,text='>>',command=lambda: self.funBrowse(delta=+1)),
        ]
        for sB in self.shiftButtons:
            sB.pack(side=tk.LEFT)
        self.saveButton=tk.Button(self.controlPanel,text='Save',command=self.funSave)
        self.saveButton.pack(side=tk.LEFT)
        self.doButton=tk.Button(self.controlPanel,fg='blue',text='DEBUG',command=self.doButton)
        self.doButton.pack(side=tk.LEFT)
        self.controlPanel.pack(side=tk.TOP)

        # this window's own canvas map, to be used by rectangles
        self.canvasMap={}
        self.picZoom=None

        # canvas the image is shown in, with its additional features
        self.picCanvas=sfCanvas(self.master,sfTag='mainView',width=180,height=180)
        self.picCanvas.setMap(createAffineMap())
        self.canvasMap[self.picCanvas.sfTag]=self.picCanvas
        # bindings for events on the canvas window
        self._bindMouse(self.picCanvas)
        self.picCanvas.bind('<Configure>',lambda ev: self.canvasConfigure(ev,canvas=self.picCanvas))

        self.picCanvas.pack(side=tk.TOP,expand=tk.YES,fill=tk.BOTH)

        # directory/images part
        class imageHandlingInfo():
            directory=os.getcwd()
            imageList=listImageFiles(directory)
            loadedFileIndex=None
            loadedFileName=None
            loadedImage=None
            shownImage=None
            zoomImage=None
            tkShownImage=None
            drawnImageIDs={}

        self.image=imageHandlingInfo()
        print self.image.imageList
        if self.image.imageList:
            self.loadImage(0)

    def funSave(self):
        for qInd,qRecta in enumerate(self.rectangles):
            print '- Saving %i/%i ...' % (qInd+1,len(self.rectangles))
            clippedImage=self.image.loadedImage.crop(qRecta.sortedTuple(integer=True))
            clippedImage.save('CLIP_%03i.jpg' % qInd,'jpeg')
        print 'Done.'

    def funBrowse(self,delta):
        nImages=len(self.image.imageList)
        if nImages>0:
            if self.image.loadedFileIndex is None:
                self.loadImage(0)
            else:
                self.loadImage((self.image.loadedFileIndex+delta+nImages)%nImages)

    def loadImage(self,nIndex):
        self.image.loadedFileIndex=nIndex
        self.image.loadedFileName=self.image.imageList[nIndex]
        print self.image.imageList[nIndex]
        # actual loading
        self.image.loadedImage=Image.open(os.path.join(self.image.directory,self.image.loadedFileName))
        self.refreshCanvas()
        #
        self.clearRectangles()
        self.refreshWindowTitle()

    def cleanMainImage(self):
        if self.picCanvas.sfTag in self.image.drawnImageIDs:
            self.picCanvas.delete(self.image.drawnImageIDs[self.picCanvas.sfTag])
            del self.image.drawnImageIDs[self.picCanvas.sfTag]

    def refreshCanvas(self):
        '''
            if there's an image loaded, scale it, prepare affine map and display it
            (garbage-collecting previous displays if any!)
            if no images, just clean the canvas
        '''
        if self.image.loadedImage is None:
            print 'LoadedImage was none: clean this'
        else:
            # find scale factor
            cvSize=(self.picCanvas.winfo_width(),self.picCanvas.winfo_height())
            scaleFactor=findRescaleFactor(self.image.loadedImage.size,cvSize)
            print 'sf=%f' % scaleFactor
            # set affine map
            self.picCanvas.setMap(createAffineMap(scaleFactor,scaleFactor))
            # rescale pic, show it
            self.cleanMainImage()
            shownSize=tuple(int(ldDim / scaleFactor) for ldDim in self.image.loadedImage.size)
            print 'shownSize:', shownSize
            self.image.shownImage=self.image.loadedImage.resize(shownSize, Image.ANTIALIAS)
            # make the tour through PIL to show image and so on
            self.image.tkShownImage=ImageTk.PhotoImage(self.image.shownImage)
            self.image.drawnImageIDs[self.picCanvas.sfTag]= \
                self.picCanvas.create_image(0,0,anchor=tk.NW,image=self.image.tkShownImage)
            #
            self.refreshRectangles()

    def refreshWindowTitle(self):
        if self.image.loadedImage is not None:
            self.master.title('Skanfixer - %s (%i/%i) %ix%ipx' % (self.image.loadedFileName,
                self.image.loadedFileIndex+1,
                len(self.image.imageList),
                self.image.loadedImage.size[0],
                self.image.loadedImage.size[1]))
        else:
            self.master.title('Skanfixer')

    def funExit(self):
        self.master.quit()

    def doButton(self):
        print 'Rectangles'
        for qInd,qRecta in enumerate(self.rectangles):
            print '%3i -> %s' % (qInd,qRecta)
            for c in qRecta.corners():
                print '    ', c
            print '     C = %s' % (','.join(qRecta.boundCanvases))


    def findCloseThing(self,point,canvas):
        '''
            determines if a point is close enough to a 'thing' (corner, ...)
            that a click there is tied to editing that 'thing'
            Returns either None or a 2-uple (c,X) with c character and X object
            character:
                'c' = corner, what follows is (rectangle,(corner_index,distance2))
                's' = side, what follows is (rectangle,(side_index,distance2))
                'r' = rectangle [general, any part of outline], (rectangle,distance2)
            TODO: this will return a dict with all types of match in any case (or empty)
        '''
        minDistance=settings['MIN_NEARCLICK_DISTANCE']
        # try and pick the nearest corner among all rectangles
        if len(self.rectangles)>0:
            possibleCorners=[(rec,rec.nearestCorner(point,canvas.mapper)) for rec in self.rectangles]
            closestCorner=sorted(possibleCorners,key=lambda p: p[1][1])[0]
            if math.sqrt(closestCorner[1][1]) <= minDistance:
                return ('c',closestCorner)
        # here should take care of side-edits
        if len(self.rectangles)>0:
            possibleMidpoints=[(rec,rec.nearestMidpoint(point,canvas.mapper)) for rec in self.rectangles]
            closestMidpoint=sorted(possibleMidpoints,key=lambda p:p[1][1])[0]
            if math.sqrt(closestMidpoint[1][1]) <= minDistance:
                return ('s',closestMidpoint)
        # here just look for a close rectangle in its whole outline
        if len(self.rectangles)>0:
            possibleRectangles=[(rec,rec.anywhereDistance(point,canvas.mapper)) for rec in self.rectangles]
            closestRectangle=sorted(possibleRectangles,key=lambda p: p[1])[0]
            if math.sqrt(closestRectangle[1]) <= minDistance:
                return ('r',closestRectangle)
        # finally, if all else fails
        return None

    def clearRectangles(self):
        for qRecta in self.rectangles:
            qRecta.disappear()
        self.rectangles=[]
        self.edit.targetRectangle=None
        self.edit.status=emINERT

    def refreshRectangles(self):
        for qRecta in self.rectangles:
            qRecta.refreshDisplay()

    def canvasMouseDown(self,event,button,canvas):
        self.edit.buttonPressed=button
        self.edit.buttonTime=time()

    def createZoomOverlay(self,canvCentreEvent,mapperToExternal):
        '''
            canvCentre = actual coords in the (picCanvas) main view
            imgCentre = corresponding coords in picture real 'external' units
        '''
        canvCentre=sfPoint(canvCentreEvent.x,canvCentreEvent.y)
        imgCentre=mapperToExternal(canvCentre)
        # delete previous zoom if any
        self.deleteZoomOverlay()
        # create zoom sfCanvas
        zwWidth=settings['ZOOM']['IMAGE_WIDTH']*settings['ZOOM']['FACTOR_X']
        zwHeight=settings['ZOOM']['IMAGE_HEIGHT']*settings['ZOOM']['FACTOR_Y']
        # after adjustments, map the point to external (real-picture) coords
        _zoomNWCorner=canvCentre.shift(-0.5*zwWidth,-0.5*zwHeight)
        # bounce on borders: check right- and left- bounce and do the best possible adjustment
        for _sizeIndex,_sizeName,_winExtent in zip([0,1],['x','y'],[zwWidth,zwHeight]):
            if _zoomNWCorner[_sizeName]>self.image.shownImage.size[_sizeIndex]-_winExtent: # right-bounce
                _zoomNWCorner[_sizeName]=self.image.shownImage.size[_sizeIndex]-_winExtent
            if _zoomNWCorner[_sizeName]<0: # left-bounce
                _zoomNWCorner[_sizeName]=0
        _zoomSECorner=_zoomNWCorner.shift(zwWidth,zwHeight)
        # create zoom overlay
        self.picZoom=sfCanvas(self.picCanvas,sfTag='zoomView',
            width=zwWidth,height=zwHeight)
        # bind events to zoom frame
        self._bindMouse(self.picZoom)
        # register zoom canvas in canvas map
        self.canvasMap[self.picZoom.sfTag]=self.picZoom
        # determine zoom position and affine map
        _fx=1.0/settings['ZOOM']['FACTOR_X']
        _fy=1.0/settings['ZOOM']['FACTOR_Y']
        _dx=imgCentre['x']-0.5*_fx*zwWidth
        _dy=imgCentre['y']-0.5*_fy*zwHeight
        self.picZoom.setMap(createAffineMap(_fx,_fy,_dx,_dy))
        # zoom overlay positioning and display
        _imgClipRegion=sfRectangle(imgCentre.shift(-0.5*settings['ZOOM']['IMAGE_WIDTH'],
                -0.5*settings['ZOOM']['IMAGE_HEIGHT']),
            imgCentre.shift(0.5*settings['ZOOM']['IMAGE_WIDTH'],
                0.5*settings['ZOOM']['IMAGE_HEIGHT']),{}).sortedTuple(integer=True)
        print _imgClipRegion
        self.image.zoomImage=ImageTk.PhotoImage(self.image.loadedImage.crop(_imgClipRegion).resize((zwWidth,zwHeight),Image.NEAREST))
        self.image.drawnImageIDs[self.picZoom.sfTag]= \
            self.picZoom.create_image(0,0,anchor=tk.NW,image=self.image.zoomImage)
        self.picZoom.place(x=_zoomNWCorner['x'],y=_zoomNWCorner['y'])
        # register and trigger redraw for all rectangles
        for qRecta in self.rectangles:
            for sfTag in self.canvasMap:
                qRecta.registerCanvas(sfTag)

    def deleteZoomOverlay(self):
        if self.picZoom:
            self.image.zoomImage=None
            for qRecta in self.rectangles:
                qRecta.deregisterCanvas(self.picZoom.sfTag)
            self.picZoom.delete(self.image.drawnImageIDs[self.picZoom.sfTag])
            del self.image.drawnImageIDs[self.picZoom.sfTag]
            del self.canvasMap[self.picZoom.sfTag]
            self.picZoom.destroy()
            self.picZoom=None

    def _bindMouse(self,canvas):
        '''
            performs some click- and motion- standard binds by packaging the canvas nature as well into the calls
        '''
        canvas.bind('<ButtonRelease-1>',lambda ev: self.canvasRelease(ev,button=1,canvas=canvas))
        canvas.bind('<ButtonRelease-2>',lambda ev: self.canvasRelease(ev,button=2,canvas=canvas))
        canvas.bind('<ButtonRelease-3>',lambda ev: self.canvasRelease(ev,button=3,canvas=canvas))
        canvas.bind('<ButtonPress-1>',lambda ev: self.canvasMouseDown(ev,button=1,canvas=canvas))
        canvas.bind('<ButtonPress-2>',lambda ev: self.canvasMouseDown(ev,button=2,canvas=canvas))
        canvas.bind('<ButtonPress-3>',lambda ev: self.canvasMouseDown(ev,button=3,canvas=canvas))
        canvas.bind('<Motion>',lambda ev: self.canvasMotion(ev,canvas=canvas))

    def canvasClick(self,event,button,canvas):
        evPoint=canvas.mapper(event)
        # handle cases depending on button pressed and previous rectangle-edit status
        if self.edit.status==emINERT:
            if button==1:
                closeThing=self.findCloseThing(evPoint,canvas)
                if closeThing is None:
                    # If it's a 'long click' the zoom overlay pops up
                    if time()-self.edit.buttonTime > (settings['MOUSE_TIMING']['LONG_CLICK_TIME_MS']/1000.0):
                        self.createZoomOverlay(event,canvas.mapper)
                    newRe=sfRectangle(evPoint,evPoint,canvasMap=self.canvasMap,color=settings['COLOR']['EDITING'])
                    newRe.decorate('handle','c',0)
                    for sfTag in self.canvasMap:
                        newRe.registerCanvas(sfTag)
                    self.rectangles.append(newRe)
                    self.edit.targetRectangle=newRe
                    self.edit.targetPoint=0
                    self.edit.undoRectangle=None
                    self.edit.status=emEDITCORNER
                elif closeThing[0] in ['c','s']:
                    # If it's a 'long click' the zoom overlay pops up
                    if time()-self.edit.buttonTime > (settings['MOUSE_TIMING']['LONG_CLICK_TIME_MS']/1000.0):
                        self.createZoomOverlay(event,canvas.mapper)
                    if closeThing[0]=='c':
                        self.edit.status=emEDITCORNER
                    elif closeThing[0]=='s':
                        self.edit.status=emEDITSIDE
                    self.edit.targetPoint=closeThing[1][1][0]
                    self.edit.targetRectangle=closeThing[1][0]
                    self.edit.targetRectangle.setColor(settings['COLOR']['EDITING'])
                    self.edit.undoRectangle=self.edit.targetRectangle.bareCopy()
            elif button==3:
                closeThing=self.findCloseThing(evPoint,canvas)
                if closeThing is None:
                    pass
                elif closeThing[0]=='c' or closeThing[0]=='r' or closeThing[0]=='s':
                    closeThing[1][0].disappear()
                    popItem(self.rectangles,closeThing[1][0])
                    self.canvasMotion(event,canvas)
        elif self.edit.status==emEDITCORNER or self.edit.status==emEDITSIDE:
            if button==1:
                self.edit.targetRectangle.setColor(settings['COLOR']['INERT'])
                self.edit.status=emINERT
                self.edit.undoRectangle=None
                self.canvasMotion(event,canvas)
                self.edit.targetRectangle.relimit(sfPoint(0,0),sfPoint(*self.image.loadedImage.size))
                self.edit.targetRectangle=None
            elif button==3:
                self.edit.targetRectangle.disappear()
                popItem(self.rectangles,self.edit.targetRectangle)
                # if possible, just undo currently-edited rectangle to former state
                if self.edit.undoRectangle is not None:
                    self.edit.undoRectangle.setColor(settings['COLOR']['INERT'])
                    for sfTag in self.canvasMap:
                        self.edit.undoRectangle.registerCanvas(sfTag)
                    self.rectangles.append(self.edit.undoRectangle)
                    self.edit.undoRectangle=None
                self.edit.targetRectangle=None
                self.edit.status=emINERT
                self.canvasMotion(event,canvas)
            self.deleteZoomOverlay()
        else:
            raise ValueError('self.edit.status')

    def canvasRelease(self,event,button,canvas):
        # mouse button released --> a 'click' operation is triggered
        self.canvasClick(event,button,canvas)
        self.edit.buttonPressed=None
        self.edit.buttonTime=time()

    def canvasMotion(self,event,canvas):
        evPoint=canvas.mapper(event)
        self.edit.cursorPos=evPoint
        #print self.edit.cursorPos
        if self.edit.status==emEDITCORNER:
            self.edit.targetRectangle.dragPoint(self.edit.targetPoint,evPoint)
        if self.edit.status==emEDITSIDE:
            self.edit.targetRectangle.dragSide(self.edit.targetPoint,evPoint)
        elif self.edit.status==emINERT:
            # temporary coloring of rectangles
            for qRec in self.rectangles:
                qRec.setColor(settings['COLOR']['INERT'])
                qRec.undecorate('handle')
            closeThing=self.findCloseThing(evPoint,canvas)
            if closeThing is not None:
                if closeThing[0]=='c':
                    closeThing[1][0].decorate('handle','c',closeThing[1][1][0])
                if closeThing[0]=='s':
                    closeThing[1][0].decorate('handle','s',closeThing[1][1][0])
                closeThing[1][0].setColor(settings['COLOR']['SELECTABLE'])

    def canvasConfigure(self,event,canvas):
        print 'CONFIGURE %i,%i (%i,%i)' % (event.width,event.height,
            canvas.winfo_width(),canvas.winfo_height())
        self.refreshCanvas()
        self.refreshRectangles()

def main():

    # standard imports
    import Tkinter as tk

    # main body
    root=tk.Tk()
    mainWindow=sfMain(root)

    root.mainloop()

if __name__=="__main__":
    main()
