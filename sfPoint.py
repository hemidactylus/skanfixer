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

    def intLabel(self):
        return '%i, %i' % tuple(int(v) for v in (self.x,self.y))

    def asTuple(self):
        return tuple((self.x,self.y))

    def copy(self):
        return sfPoint(self.x,self.y)

    def distance2(self,other,mapper):
        '''
            returns the squared distance between the two points (Euclidean metric)
            ** All of this after applying a reverse affine map **
        '''
        _mo=mapper(other,'r')
        _ms=mapper(self,'r')
        return (((_ms.x-_mo.x)**2)+((_ms.y-_mo.y)**2))

    def midpoint(self,other):
        '''
            returns the mid point between this point and another
        '''
        return sfPoint(0.5*(self.x+other.x),0.5*(self.y+other.y))

    def distanceToAxisSegment(self,segment,mapper):
        '''
            Given a segment as a 2-item array of sfPoints, assumed to lie
            EITHER ON THE x or THE y AXIS, this gives the distance to it
            ** All of this after applying a reverse affine map **
        '''
        _ms=mapper(self,'r')
        _mseg=[mapper(sit,'r') for sit in  segment]
        # distance from self to the segment segment. Horiz or vert?
        constAxis='x' if _mseg[0]['x']==_mseg[1]['x'] else 'y'
        varAxis='y' if constAxis=='x' else 'x'
        thisDistance=(_ms[constAxis]-_mseg[0][constAxis])**2.0
        if _ms[varAxis]<=min(cS[varAxis] for cS in _mseg) or _ms[varAxis]>=max(cS[varAxis] for cS in _mseg):
            thisDistance+=min([(cS[varAxis]-_ms[varAxis])**2.0 for cS in _mseg])
        return thisDistance

    def shift(self,deltaX,deltaY):
        '''
            Returns a new sfPoint with coordinates additively changed by the provided amounts
        '''
        return sfPoint(self.x+deltaX,self.y+deltaY)

    def rescale(self,factorX,factorY,limitValuesX=(None,None),limitValuesY=(None,None)):
        '''
            Returns a new sfPoint with the coordinates expanded by the given
            factors, with optional limiting upper value (if not None).

            For each dimension, the tuple is (minVal,maxVal). Boundaries are allowed.

        '''
        _x=self.x*factorX
        _y=self.y*factorY
        if limitValuesX[0] is not None:
            if _x < limitValuesX[0]:
                _x=limitValuesX[0]
        if limitValuesX[1] is not None:
            if _x > limitValuesX[1]:
                _x=limitValuesX[1]
        if limitValuesY[0] is not None:
            if _y < limitValuesY[0]:
                _y=limitValuesY[0]
        if limitValuesY[1] is not None:
            if _y > limitValuesY[1]:
                _y=limitValuesY[1]
        return sfPoint(_x,_y)

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
