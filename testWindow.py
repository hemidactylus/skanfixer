'''
    rectangle test window
'''

# edit modes
emINERT=0
emCREATING=1

# standard imports
import Tkinter as tk
from PIL import Image, ImageTk
import os

# skanfixer imports
from sfPoint import sfPoint
from sfRectangle import sfRectangle
from sfCanvas import sfCanvas
from sfAffineMaps import createAffineMap

class testWindow():

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
                    - edit.targetCorner:    if shaping a recta, this is the grabbed corner index

                * rectangles:               a list of rectangles (with their bindings and everything)
        '''

        # handy miniclasses for datamembers
        class sfEditStatus():
            cursorPos=sfPoint()
            status=emINERT
            targetRectangle=None
            targetCorner=0

        # setting up the data members
        self.rectangles=[]
        self.edit=sfEditStatus()

        print 'Init.'

        # Window layout
        self.master=master
        self.master.geometry('200x200')
        # controls are in a frame
        self.controlPanel=tk.Frame(self.master)
        self.quitButton=tk.Button(self.controlPanel,text='Exit',command=self.funExit)
        self.quitButton.pack(side=tk.LEFT)
        self.doButton=tk.Button(self.controlPanel,fg='blue',text='"Load"',command=self.doLoad)
        self.doButton.pack(side=tk.LEFT)
        self.doButton=tk.Button(self.controlPanel,fg='blue',text='Add r',command=self.testAdd)
        self.doButton.pack(side=tk.LEFT)
        self.doButton=tk.Button(self.controlPanel,fg='blue',text='Remove r',command=self.testRemove)
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

    def doLoad(self):
        self.picCanvas.setMap(createAffineMap())
        p1=sfPoint(40.0,80.0)
        p2=sfPoint(120.0,60.0)
        print p1,p2
        self.r1=sfRectangle(p1,p2,canvasMap=self.canvasMap,color='red')
        print self.r1
        print p1['x']
        print self.r1.corners()
        print self.r1.sortedTuple()
        self.r1.registerCanvas('mainView')

    def canvasClick(self,event,button):
        evPoint=self.picCanvas.mapper(event)
        if self.edit.status==emINERT:
            newRe=sfRectangle(evPoint,evPoint,canvasMap=self.canvasMap,color='blue')
            newRe.registerCanvas('mainView')
            self.rectangles.append(newRe)
            self.edit.targetRectangle=newRe
            self.edit.targetCorner=0
            self.edit.status=emCREATING
        elif self.edit.status==emCREATING:
            self.edit.targetRectangle.setColor('red')
            self.edit.status=emINERT
        else:
            raise ValueError('self.edit.status')

    def canvasRelease(self,event,button):
        evPoint=self.picCanvas.mapper(event)

    def canvasMotion(self,event):
        evPoint=self.picCanvas.mapper(event)
        self.edit.cursorPos=evPoint
        #print self.edit.cursorPos
        if self.edit.status==emCREATING:
            self.edit.targetRectangle.dragPoint(self.edit.targetCorner,evPoint)

    def canvasConfigure(self,event):
        print 'CONFIGURE %i,%i' % (event.width,event.height)
        pass

    def testAdd(self):
        pass

    def testRemove(self):
        pass

def main():

    # standard imports
    import Tkinter as tk

    # main body
    root=tk.Tk()
    testwindow=testWindow(root)

    root.mainloop()

if __name__=="__main__":
    main()
