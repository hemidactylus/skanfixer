import tkinter as tk
import tkinter.simpledialog as simpledialog

class sfInputBox(simpledialog.Dialog):

    def __init__(self,*pargs,**kwargs):
        if 'prevValue' in kwargs:
            self.prevValue=kwargs['prevValue']
            del kwargs['prevValue']
        else:
            self.prevValue=None
        simpledialog.Dialog.__init__(self,*pargs,**kwargs)

    def body(self, master):

        tk.Label(master, text="Offset: ").grid(row=0)

        self.entry = tk.Entry(master,bg='white')
        if self.prevValue is not None:
            self.entry.insert(0,str(self.prevValue))
            self.entry.select_range(0,tk.END)

        self.entry.grid(row=0, column=1)
        return self.entry # initial focus

    def apply(self):
        try:
            self.result = int(self.entry.get())
        except:
            self.result = None
