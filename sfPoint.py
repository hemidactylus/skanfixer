'''
    class sfPoint: pair (x,y) of floating-point coordinates for all uses within skanfixer
'''

class sfPoint():

    def __init__(self,x,y):
        self.x=x
        self.y=y

    def __str__(self):
        return 'sfPoint[%f,%f]' % (self.x,self.y)

    def __repr__(self):
        return self.__str__()

    def asTuple(self):
        return tuple(x,y)

    def __getitem__(self,idx):
        if idx=='x':
            return self.x
        elif idx=='y':
            return self.y
        else:
            raise KeyError(idx)
