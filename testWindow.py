'''
    rectangle test window
'''

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

        print 'Init.'

        # Window layout
        self.master=master
        self.master.geometry('200x200')
        # controls are in a frame
        self.controlPanel=tk.Frame(self.master)
        self.quitButton=tk.Button(self.controlPanel,text='Exit',command=self.funExit)
        self.quitButton.pack(side=tk.LEFT)
        self.doButton=tk.Button(self.controlPanel,fg='blue',text='Do 1',command=self.funDo)
        self.doButton.pack(side=tk.LEFT)
        self.doButton2=tk.Button(self.controlPanel,fg='blue',text='Do 2',command=self.funDo2)
        self.doButton2.pack(side=tk.LEFT)
        self.doButton2=tk.Button(self.controlPanel,fg='blue',text='Del',command=self.funDoClear)
        self.doButton2.pack(side=tk.LEFT)
        self.controlPanel.pack(side=tk.TOP)

        # this window's own canvas map, to be used by rectangles
        self.canvasMap={}

        # canvas the image is shown in, with its additional features
        self.picCanvas=sfCanvas(self.master,sfTag='mainView',width=180,height=180)
        self.picCanvas.setMaps(createAffineMap())
        self.canvasMap[self.picCanvas.sfTag]=self.picCanvas

        self.picCanvas.pack(side=tk.TOP,expand=tk.YES,fill=tk.BOTH)

    def funExit(self):
        self.master.quit()

    def funDo(self):
        self.picCanvas.setMaps(createAffineMap())
        p1=sfPoint(40.0,80.0)
        p2=sfPoint(120.0,60.0)
        print p1,p2
        self.r1=sfRectangle(p1,p2,canvasMap=self.canvasMap,color='red')
        print self.r1
        print p1['x']
        print self.r1.corners()
        print self.r1.sortedTuple()
        self.r1.registerCanvas('mainView')

    def funDo2(self):
        self.picCanvas.setMaps(createAffineMap(fucktor=0.5))
        p1=sfPoint(40.0,80.0)
        p2=sfPoint(120.0,60.0)
        print p1,p2
        self.r1=sfRectangle(p1,p2,canvasMap=self.canvasMap,color='blue')
        print self.r1
        print p1['x']
        print self.r1.corners()
        print self.r1.sortedTuple()
        self.r1.registerCanvas('mainView')

    def funDoClear(self):
        self.r1.deregisterCanvas('mainView')

def main():

    # standard imports
    import Tkinter as tk

    # main body
    root=tk.Tk()
    testwindow=testWindow(root)

    root.mainloop()

if __name__=="__main__":
    main()
