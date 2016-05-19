''' SelRectangle: a selection rectangle as embedded into a
    picture widget.
'''

class SelRectangle():

    def __init__(self,corner1,corner2):
        self.xs=[corner1[0],corner2[0]]
        self.ys=[corner1[1],corner2[1]]

    def asTuple(self,counterFactor=1.0):
        returnee = (self.xs[0],self.ys[0],self.xs[1],self.ys[1])
        return tuple(int(x *counterFactor) for x in returnee)

    def sort(self):
        ''' in-place shuffling of coordinates, ensures proper ordering
        '''
        self.xs=[min(self.xs),max(self.xs)]
        self.ys=[min(self.ys),max(self.ys)]

    def __str__(self):
        return '! ' + str(self.asTuple()) + ' !'

    def hasOnEdge(self,cx,cy,tol):
        '''
            return True if the given point lies within TOL (max in either dir)
            from the rectangle's edge
        '''
        mxs=[min(self.xs),max(self.xs)]
        mys=[min(self.ys),max(self.ys)]
        if cx+tol>=mxs[0] and cx-tol<=mxs[1]:
            # we are in the right vert strip
            if any(abs(cy-somey)<=tol for somey in mys):
                return True
        if cy+tol>=mys[0] and cy-tol<=mys[1]:
            # we are in the right horiz strip
            if any(abs(cx-somex)<=tol for somex in mxs):
                return True
        return False
