'''
    sfCanvas: a special Canvas that retains some enriched features,
    most notably affine maps and a tag system
'''

import tkinter

class sfCanvas(tkinter.Canvas):

    def __init__(self, *pargs, **kwargs):
        '''
            simply adds a keyword argument 'sfTag' to the init
        '''
        if 'sfTag' not in kwargs:
            kwargs['sfTag']='NOT_SET'
        self.sfTag=kwargs['sfTag']
        del kwargs['sfTag']
        tkinter.Canvas.__init__(self,*pargs,**kwargs)

    def setMap(self, coordinateMapper=None):
        '''
            allows setting a coordinate mapper object to the canvas
        '''
        self.mapper=coordinateMapper
