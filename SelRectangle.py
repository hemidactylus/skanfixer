''' SelRectangle: a selection rectangle as embedded into a
    picture widget.
'''

class SelRectangle():

    def __init__(self,corner1,corner2,factor=1.0):
        self.xs=[corner1[0]*factor,corner2[0]*factor]
        self.ys=[corner1[1]*factor,corner2[1]*factor]

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