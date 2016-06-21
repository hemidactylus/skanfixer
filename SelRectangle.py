''' SelRectangle: a selection rectangle as embedded into a
    picture widget.
'''

class SelRectangle():

    def __init__(self,corner1,corner2):
        self.xs=[corner1[0],corner2[0]]
        self.ys=[corner1[1],corner2[1]]
        self.rectaID={}

    def unshow(self,qcanvas):
        print 'TryingToUnshow ', qcanvas._name, 
        if qcanvas._name in self.rectaID:
            print 'OK'
            qcanvas.delete(self.rectaID[qcanvas._name])
            del self.rectaID[qcanvas._name]
        else:
            print 'no'

    def show(self,qcanvas,factor=1.0,width=4,color='red',offset=(0,0)):
        #self.unshow(qcanvas)
        self.sort()
        self.rectaID[qcanvas._name]=qcanvas.create_rectangle(self.asTuple(factor,offset),width=width,outline=color)

    def asTuple(self,counterFactor=1.0,offset=(0,0)):
        returnee = (self.xs[0],self.ys[0],self.xs[1],self.ys[1])
        result =tuple(int((x-dx)*counterFactor) for x,dx in zip(returnee,offset*2))
        return result

    def sort(self):
        '''
            in-place shuffling of coordinates, ensures proper ordering
        '''
        self.xs=[min(self.xs),max(self.xs)]
        self.ys=[min(self.ys),max(self.ys)]

    def __str__(self):
        return '! (%i,%i)-(%i,%i) !' % self.asTuple()

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

    def hasOnCorner(self,cx,cy,tol):
        '''
            return a 2uple marking the corner (0/1,0/1)
            if the rectangle has an edge close to the given point,
            or None,None if nothing matches
        '''
        for cox,coy in [(a,b) for a in [0,1] for b in [0,1]]:
            if abs(cx-self.xs[cox])<=tol and abs(cy-self.ys[coy])<=tol:
                return (cox,coy)
        return None
