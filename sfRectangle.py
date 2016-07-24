'''
    Class sfRectangle for multi-rectangle selection.
    Features a multiple map to canvases, each with its own affine map from the real coordinates
    to the ones for the canvas.
'''

from sfPoint import sfPoint

# source-point-xy-indices-pairs:
XY_IND_SEQ=((0,0),(1,0),(1,1),(0,1))
'''
    this means: the second corner of a rectangle -> (1,0)
        -> the x is the one of the second point (1), the y is the one of the first point (0)
'''

class sfRectangle():
    
    def __init__(self,p1,p2):
        self.srcPoints=(p1,p2)

    def __str__(self):
        return 'sfRectangle{%s ; %s}' % (self.srcPoints)

    def corners(self):
        '''
            returns all four corners as a 4-item array of sfPoints,
            arranged in the order specified by XY_IND_SEQ
        '''
        return [sfPoint(self.srcPoints[ix]['x'],self.srcPoints[iy]['y'],) for ix,iy in XY_IND_SEQ]

    def sortedTuple(self):
        '''
            returns a 4-item tuple of sorted (x_min,y_min,x_max,y_max) values for use with Canvas.create_rectangle
        '''
        return tuple([fun([pt[dim] for pt in self.srcPoints]) for fun in [min,max] for dim in ['x','y']])
    
