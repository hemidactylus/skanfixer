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

# skanfixer imports
from sfPoint import sfPoint
from sfRectangle import sfRectangle
from sfCanvas import sfCanvas
from sfAffineMaps import createAffineMap
from sfSettings import settings
from sfUtilities import popItem

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

        # setting up the data members
        self.rectangles=[]
        self.edit=sfEditStatus()

        print 'Init.'

        # Window layout
        self.master=master
        self.master.geometry('500x500')
        # controls are in a frame
        self.controlPanel=tk.Frame(self.master)
        self.quitButton=tk.Button(self.controlPanel,text='Exit',command=self.funExit)
        self.quitButton.pack(side=tk.LEFT)
        self.doButton=tk.Button(self.controlPanel,fg='blue',text='DEBUG',command=self.doButton)
        self.doButton.pack(side=tk.LEFT)
        self.controlPanel.pack(side=tk.TOP)

        # this window's own canvas map, to be used by rectangles
        self.canvasMap={}

        # canvas the image is shown in, with its additional features
        self.picCanvas=sfCanvas(self.master,sfTag='mainView',width=180,height=180)
        self.picCanvas.setMap(createAffineMap())
        self.canvasMap[self.picCanvas.sfTag]=self.picCanvas
        # bindings for events on the canvas window
        self.picCanvas.bind('<Button-1>',lambda ev: self.canvasClick(ev,button=1))
        self.picCanvas.bind('<Button-2>',lambda ev: self.canvasClick(ev,button=2))
        self.picCanvas.bind('<Button-3>',lambda ev: self.canvasClick(ev,button=3))
        self.picCanvas.bind('<ButtonRelease-1>',lambda ev: self.canvasRelease(ev,button=1))
        self.picCanvas.bind('<ButtonRelease-2>',lambda ev: self.canvasRelease(ev,button=2))
        self.picCanvas.bind('<ButtonRelease-3>',lambda ev: self.canvasRelease(ev,button=3))
        self.picCanvas.bind('<Motion>',self.canvasMotion)
        self.picCanvas.bind('<Configure>',self.canvasConfigure)

        self.picCanvas.pack(side=tk.TOP,expand=tk.YES,fill=tk.BOTH)

    def funExit(self):
        self.master.quit()

    def doButton(self):
        print 'REKTAs'
        for r in self.rectangles:
            print r
            for c in r.corners():
                print '    ', c

    def findCloseThing(self,point):
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
        # try and pick the nearest corner among all rectangles
        if len(self.rectangles)>0:
            possibleCorners=[(rec,rec.nearestCorner(point)) for rec in self.rectangles]
            closestCorner=sorted(possibleCorners,key=lambda p: p[1][1])[0]
            if math.sqrt(closestCorner[1][1]) <= settings['MIN_NEARCLICK_DISTANCE']:
                return ('c',closestCorner)
        # here should take care of side-edits
        if len(self.rectangles)>0:
            possibleMidpoints=[(rec,rec.nearestMidpoint(point)) for rec in self.rectangles]
            closestMidpoint=sorted(possibleMidpoints,key=lambda p:p[1][1])[0]
            if math.sqrt(closestMidpoint[1][1]) <= settings['MIN_NEARCLICK_DISTANCE']:
                return ('s',closestMidpoint)
        # here just look for a close rectangle in its whole outline
        if len(self.rectangles)>0:
            possibleRectangles=[(rec,rec.anywhereDistance(point)) for rec in self.rectangles]
            closestRectangle=sorted(possibleRectangles,key=lambda p: p[1])[0]
            if math.sqrt(closestRectangle[1]) <= settings['MIN_NEARCLICK_DISTANCE']:
                return ('r',closestRectangle)
        # finally, if all else fails
        return None

    def canvasClick(self,event,button):
        evPoint=self.picCanvas.mapper(event)
        if self.edit.status==emINERT:
            if button==1:
                closeThing=self.findCloseThing(evPoint)
                if closeThing is None:
                    newRe=sfRectangle(evPoint,evPoint,canvasMap=self.canvasMap,color=settings['COLOR']['EDITING'])
                    newRe.decorate('handle','c',0)
                    newRe.registerCanvas('mainView')
                    self.rectangles.append(newRe)
                    self.edit.targetRectangle=newRe
                    self.edit.targetPoint=0
                    self.edit.status=emEDITCORNER
                elif closeThing[0] in ['c','s']:
                    if closeThing[0]=='c':
                        self.edit.status=emEDITCORNER
                    elif closeThing[0]=='s':
                        self.edit.status=emEDITSIDE
                    self.edit.targetPoint=closeThing[1][1][0]
                    self.edit.targetRectangle=closeThing[1][0]
                    self.edit.targetRectangle.setColor(settings['COLOR']['EDITING'])
                    self.edit.undoRectangle=self.edit.targetRectangle.bareCopy()
            elif button==3:
                closeThing=self.findCloseThing(evPoint)
                if closeThing is None:
                    pass
                elif closeThing[0]=='c' or closeThing[0]=='r' or closeThing[0]=='s':
                    closeThing[1][0].disappear()
                    popItem(self.rectangles,closeThing[1][0])
                    self.canvasMotion(event)
        elif self.edit.status==emEDITCORNER or self.edit.status==emEDITSIDE:
            if button==1:
                self.edit.targetRectangle.setColor(settings['COLOR']['INERT'])
                self.edit.status=emINERT
                self.canvasMotion(event)
            elif button==3:
                self.edit.targetRectangle.disappear()
                popItem(self.rectangles,self.edit.targetRectangle)
                # if possible, just undo currently-edited rectangle to former state
                if self.edit.undoRectangle is not None:
                    self.edit.undoRectangle.setColor(settings['COLOR']['INERT'])
                    self.edit.undoRectangle.registerCanvas('mainView')
                    self.rectangles.append(self.edit.undoRectangle)
                    self.edit.undoRectangle=None
                self.edit.targetRectangle=None
                self.edit.status=emINERT
                self.canvasMotion(event)
        else:
            raise ValueError('self.edit.status')
        print 'rectangles = %i' % len(self.rectangles)

    def canvasRelease(self,event,button):
        evPoint=self.picCanvas.mapper(event)

    def canvasMotion(self,event):
        evPoint=self.picCanvas.mapper(event)
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
            closeThing=self.findCloseThing(evPoint)
            if closeThing is not None:
                if closeThing[0]=='c':
                    closeThing[1][0].decorate('handle','c',closeThing[1][1][0])
                if closeThing[0]=='s':
                    closeThing[1][0].decorate('handle','s',closeThing[1][1][0])
                closeThing[1][0].setColor(settings['COLOR']['SELECTABLE'])

    def canvasConfigure(self,event):
        print 'CONFIGURE %i,%i' % (event.width,event.height)
        pass

def main():

    # standard imports
    import Tkinter as tk

    # main body
    root=tk.Tk()
    mainWindow=sfMain(root)

    root.mainloop()

if __name__=="__main__":
    main()
