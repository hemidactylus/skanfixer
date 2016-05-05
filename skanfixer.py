#!/usr/bin/env python

""" Skanfixer, semi-automatic handling of extracting photos from scanned
    pages. Author: hemidactylus
"""

import os, sys
import Tkinter
from PIL import Image, ImageTk

class MainWindow():

    recta=[None]*4
    recid=None

    def refreshRecta(self):
        if any([x is None for x in self.recta]):
            print 'Abo', self.recta
            if self.recid is not None:
                self.pic.delete(self.recid)
            self.recid=None
            return
        else:
            if self.recid is not None:
                self.pic.delete(self.recid)
            self.recid=self.pic.create_rectangle(tuple(coo*self.factor for coo in self.recta),width=4,outline='red')
            print 'Rekta', self.recta
    def exiter(self):
        self.master.quit()
    def clickerL(self,event):
        print 'ClickerL: %i,%i' % (event.x,event.y)
        self.recta[0]=int(event.x/self.factor)
        self.recta[1]=int(event.y/self.factor)
        self.refreshRecta()
    def clickerR(self,event):
        print 'ClickerR: %i,%i' % (event.x,event.y)
        self.recta[2]=int(event.x/self.factor)
        self.recta[3]=int(event.y/self.factor)
        self.refreshRecta()
    def __init__(self,master):
        self.master=master
        self.qui=Tkinter.Button(self.master,text='Exit',command=self.exiter)
        self.qui.pack(side=Tkinter.TOP)
        self.master.geometry('+%d+%d' % (900,100))
    def dis(self,fil):
        self.but=Tkinter.Button(self.master,fg='blue',text='Click',command=self.clip)
        self.but.pack(side=Tkinter.TOP)
        self.image1=Image.open(fil)
        #
        self.factor=0.1
        self.tsize=(int(self.image1.size[0]*self.factor),int(self.image1.size[1]*self.factor))
        self.image_scaled=self.image1.resize(self.tsize)
        #
        self.tkpi=ImageTk.PhotoImage(self.image_scaled)
        self.pic=Tkinter.Canvas(self.master,width=self.tsize[0],height=self.tsize[1])
        self.pic.create_image(0,0,anchor=Tkinter.NW,image=self.tkpi)
        self.pic.bind('<Button-1>',self.clickerL)
        self.pic.bind('<Button-3>',self.clickerR)
        self.pic.pack(side=Tkinter.TOP)
    def clip(self):
        if any([x is None for x in self.recta]):
            print 'S Abo'
            return
        else:
            print 'Saving... ',
            nimg=self.image1.crop(self.recta)
            nimg.save('CLIP.jpg','jpeg')
            print 'Done.'
    def title(self,tt):
        self.master.title(tt)

# main body
root=Tkinter.Tk()
f='image.jpg'
mS=MainWindow(root)
mS.dis(f)
mS.title('Skanfixer')
root.mainloop()
