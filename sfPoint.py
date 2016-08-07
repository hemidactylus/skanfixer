'''
    class sfPoint: pair (x,y) of floating-point coordinates for all uses within skanfixer
'''

class sfPoint():

    def __init__(self,x=0,y=0):
        self.x=float(x)
        self.y=float(y)

    def __str__(self):
        return 'sfPoint[%f,%f]' % (self.x,self.y)

    def __repr__(self):
        return self.__str__()

    def asTuple(self):
        return tuple(x,y)

    def copy(self):
        return sfPoint(self.x,self.y)

    def distance2(self,other):
        '''
            returns the squared distance between the two points (Euclidean metric)
        '''
        return (((self.x-other.x)**2)+((self.y-other.y)**2))

    def midpoint(self,other):
        '''
            returns the mid point between this point and another
        '''
        return sfPoint(0.5*(self.x+other.x),0.5*(self.y+other.y))

    def distanceToAxisSegment(self,segment):
        '''
            Given a segment as a 2-item array of sfPoints, assumed to lie
            EITHER ON THE x or THE y AXIS, this gives the distance to it
        '''
        # distance from self to the segment segment. Horiz or vert?
        constAxis='x' if segment[0]['x']==segment[1]['x'] else 'y'
        varAxis='y' if constAxis=='x' else 'x'
        thisDistance=(self[constAxis]-segment[0][constAxis])**2.0
        if self[varAxis]<=min(cS[varAxis] for cS in segment) or self[varAxis]>=max(cS[varAxis] for cS in segment):
            thisDistance+=min([(cS[varAxis]-self[varAxis])**2.0 for cS in segment])
        return thisDistance

    def shift(self,deltaX,deltaY):
        '''
            Returns a new sfPoint with coordinates additively changed by the provided amounts
        '''
        return sfPoint(self.x+deltaX,self.y+deltaY)

    def __getitem__(self,idx):
        if idx=='x':
            return self.x
        elif idx=='y':
            return self.y
        else:
            raise KeyError(idx)

    def __setitem__(self,idx,value):
        if idx=='x':
            self.x=value
        elif idx=='y':
            self.y=value
        else:
            raise KeyError(idx)
