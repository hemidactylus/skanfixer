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
        self.doButton=tk.Button(self.controlPanel,fg='blue',text='Do',command=self.funDo)
        self.doButton.pack(side=tk.LEFT)
        self.controlPanel.pack(side=tk.TOP)

        # canvas the image is shown in
        self.picCanvas=tk.Canvas(self.master,width=180,height=180)
        self.picCanvas.pack(side=tk.TOP,expand=tk.YES,fill=tk.BOTH)

    def funExit(self):
        self.master.quit()

    def funDo(self):
        p1=sfPoint(10.0,20.0)
        p2=sfPoint(30.0,15.0)
        print p1,p2
        r1=sfRectangle(p1,p2)
        print r1
        print p1['x']
        print r1.corners()
        print r1.sortedTuple()

def main():

    # standard imports
    import Tkinter as tk

    # main body
    root=tk.Tk()
    testwindow=testWindow(root)

    root.mainloop()

if __name__=="__main__":
    main()
