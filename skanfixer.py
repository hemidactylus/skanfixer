#!/usr/bin/env python

"""AAA
"""

import os, sys
import Tkinter
from PIL import Image, ImageTk

class Shower():

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
            self.recid=self.pic.create_rectangle(self.recta,width=4,outline='red')
    def exiter(self):
        self.master.quit()
    def clickerL(self,event):
        print 'ClickerL: %i,%i' % (event.x,event.y)
        self.recta[0]=event.x
        self.recta[1]=event.y
        self.refreshRecta()
    def clickerR(self,event):
        print 'ClickerR: %i,%i' % (event.x,event.y)
        self.recta[2]=event.x
        self.recta[3]=event.y
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
        self.tkpi=ImageTk.PhotoImage(self.image1)
        self.pic=Tkinter.Canvas(self.master,width=self.image1.size[0],height=self.image1.size[1])
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
f='gom2.jpg'
mS=Shower(root)
mS.dis(f)
mS.title('Test')
root.mainloop()
