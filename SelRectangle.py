''' SelRectangle: a selection rectangle as embedded into a
    picture widget.
'''

class SelRectangle():

    def __init__(self):
        self.id=None
        self.xs=[None]*2
        self.ys=[None]*2

    def asTuple(self):
        return (self.xs[0],self.ys[0],self.xs[1],self.ys[1])

    def sort(self):
        ''' in-place shuffling of coordinates, ensures proper ordering
        '''
        for ar in [self.xs,self.ys]:
            ar=[min(ar),max(ar)]
