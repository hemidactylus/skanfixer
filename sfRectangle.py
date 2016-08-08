'''
    Class sfRectangle for multi-rectangle selection.
    Features a multiple map to canvases, each with its own affine map from the real coordinates
    to the ones for the canvas.
'''

from sfPoint import sfPoint
from sfSettings import settings

# source-point-xy-indices-pairs:
XY_IND_SEQ=((0,0),(1,0),(1,1),(0,1))
'''
    this means: the second corner of a rectangle -> (1,0)
        -> the x is the one of the second point (1), the y is the one of the first point (0)
'''
# side-indices for drag-side
CI_SID_SEQ=((0,'y'),(1,'x'),(1,'y'),(0,'x'))
'''
    this means: the second side is (1,'x'):
        -> when altering the second side, set the 'x' of the second (1) point.
'''

class sfRectangle():
    
    def __init__(self,p1,p2,canvasMap,color='red'):
        self.srcPoints=(p1.copy(),p2.copy())
        self.boundCanvases=set()
        self.canvasMap=canvasMap
        self.drawingIDs={}
        self.color=color
        self.decorations={}

    def setColor(self,color='red'):
        if self.color!=color:
            self.color=color
            self.refreshDisplay()

    def __str__(self):
        return 'sfRectangle{%s ; %s}' % (self.srcPoints)

    def corners(self):
        '''
            returns all four corners as a 4-item array of sfPoints,
            arranged in the order specified by XY_IND_SEQ
        '''
        return [sfPoint(self.srcPoints[ix]['x'],self.srcPoints[iy]['y'],) for ix,iy in XY_IND_SEQ]

    def nearestCorner(self,oPoint):
        '''
            returns a 2-uple (index,distance2) of the corner (out of four)
            which is closest to the provided point
        '''
        pDistances=[oPoint.distance2(corner) for corner in self.corners()]
        return sorted(enumerate(pDistances),key=lambda x: x[1])[0]

    def nearestMidpoint(self,oPoint):
        '''
            returns a 2-uple (index,distance2) of the midpoint (out of four, indexed
            as n -> between points n and (n+1)%4)
            which is closest to the provided point
        '''
        sCorners=list(self.corners())
        mDistances=[oPoint.distance2(corner1.midpoint(corner2)) for corner1,corner2 in zip(sCorners,sCorners[1:]+sCorners[0:1])]
        return sorted(enumerate(mDistances),key=lambda x: x[1])[0]

    def anywhereDistance(self,oPoint):
        '''
            returns a 'distance to rectangle', defined as the min distance
            between any point on the rectangle outline and the given oPoint
        '''
        cCorners=list(self.corners())
        distances=[]
        for cSegment in zip(cCorners,cCorners[1:]+cCorners[0:1]):
            distances.append(oPoint.distanceToAxisSegment(cSegment))
        return min(distances)

    def sortedTuple(self):
        '''
            returns a 4-item tuple of sorted (x_min,y_min,x_max,y_max) values for use with Canvas.create_rectangle
        '''
        return tuple([fun([pt[dim] for pt in self.srcPoints]) for fun in [min,max] for dim in ['x','y']])

    def decorate(self,tag,decType,decIndex):
        '''
            adds a decoration - a graphical gizmo - to the representation of the rectangle.
            tag is used for subsequent undecoration
            decType='c' or 's' for corner or side resp.
            decIndex is a 0-3 index to specify decoration position.

            This call automatically triggers redisplay on all attached canvases
        '''
        if decType in ['c','s']:
            self.decorations[tag]={'type':decType, 'index': decIndex, 'drawingIDs':{}}
            self.refreshDisplay()
        else:
            raise ValueError(decType)

    def undecorate(self,tag):
        '''
            Removes a decoration from the decorations-set of this rectangle,
            invoking redraws as necessary
        '''
        if tag in self.decorations:
            self.disappear()
            del self.decorations[tag]
            self.refreshDisplay()

    def registerCanvas(self,canTag):
        '''
            binds a new canvas to this rectangle by means of this rectangle's own dict
            from canvas tags to canvas objects
        '''
        self.boundCanvases.add(canTag)

        # display this rectangle using the map and going onto the canvas
        self.drawRectangle(canTag)

    def dragPoint(self,pointIndex,newPoint):
        '''
            changes the position of one corner of the rectangle and automatically drags the rest
            of the representation along. Invokes the refreshes for all registered canvases.
            pointIndex refers to the same indexing as XY_IND_SEQ
        '''
        xindex=XY_IND_SEQ[pointIndex][0]
        yindex=XY_IND_SEQ[pointIndex][1]
        newPts=list(self.srcPoints)
        newPts[xindex].x=newPoint.x
        newPts[yindex].y=newPoint.y
        self.srcPoints=tuple(newPts)
        self.refreshDisplay()

    def dragSide(self,sideIndex,newPoint):
        '''
            changes the position of a side of the rectangle and automatically drags the rest
            of the representation along.
            This means changing just on coordinate of just one of the points.
            Invokes the refreshes for all registered canvases.
            pointIndex refers to the same indexing as XY_IND_SEQ
        '''
        ptindex=CI_SID_SEQ[sideIndex][0]
        coord=CI_SID_SEQ[sideIndex][1]
        newPts=list(self.srcPoints)
        newPts[ptindex][coord]=newPoint[coord]
        self.srcPoints=tuple(newPts)
        self.refreshDisplay()

    def refreshDisplay(self):
        '''
            Re-displays on all registered canvases
        '''
        for canv in self.boundCanvases:
            self.drawRectangle(canv)


    def drawRectangle(self,canvasTag):
        '''
            uses the affine map to draw the rectangle onto the required canvas
        '''

        targetCanvas=self.canvasMap[canvasTag] # is a sfCanvas
        coordMapper=self.canvasMap[canvasTag].mapper # is a mapper function sfPoint -> sfPoint

        # destroy a previously shown rectangle if necessary!
        self.unshowRectangle(canvasTag)

        # rewrite this with a 'map' and a *pts
        mapRect=sfRectangle(coordMapper(self.srcPoints[0],'r'),coordMapper(self.srcPoints[1],'r'),{})
        drawingID=targetCanvas.create_rectangle(mapRect.sortedTuple(),width=3,outline=self.color)
        self.drawingIDs[canvasTag]=drawingID
        # handle decorations attached to this rectangle
        for dk,dv in self.decorations.iteritems():
            print 'DecoDrawing %s' % dk
            dv['drawingIDs'][canvasTag]=self.drawDecoration(targetCanvas,dv['type'],dv['index'])

    def drawDecoration(self,tCanvas,dType,dIndex):
        '''
            actually draws the decoration to the rectangle and returns the drawing ID to the caller
        '''
        coordMapper=tCanvas.mapper # is a mapper function sfPoint -> sfPoint
        if dType=='c':
            canvCentre=coordMapper(self.corners()[dIndex],'r') # this is a sfPoint
            decRect=sfRectangle(canvCentre.shift( \
                -settings['CORNER_DRAG_HANDLE_SIZE'],-settings['CORNER_DRAG_HANDLE_SIZE']), \
                canvCentre.shift(+settings['CORNER_DRAG_HANDLE_SIZE'],+settings['CORNER_DRAG_HANDLE_SIZE']),{})
            return tCanvas.create_rectangle(decRect.sortedTuple(),width=0,fill=self.color)
        elif dType=='s':
            rCorners=self.corners()
            canvCentre=coordMapper(rCorners[dIndex].midpoint(rCorners[(dIndex+1)%4]),'r') # this is a sfPoint
            polyVertices=tuple(canvCentre.shift(-settings['SIDE_DRAG_HANDLE_SIZE'],0).asTuple()+ \
                               canvCentre.shift(0,+settings['SIDE_DRAG_HANDLE_SIZE']).asTuple()+ \
                               canvCentre.shift(+settings['SIDE_DRAG_HANDLE_SIZE'],0).asTuple()+ \
                               canvCentre.shift(0,-settings['SIDE_DRAG_HANDLE_SIZE']).asTuple())
            return tCanvas.create_polygon(*polyVertices,width=0,fill=self.color)

    def disappear(self):
        '''
            undraw the rectangle from all canvases where it is registered and drawn
        '''
        for canvTag in self.canvasMap:
            self.unshowRectangle(canvTag)

    def unshowRectangle(self,canvasTag):
        targetCanvas=self.canvasMap[canvasTag] # is a sfCanvas
        if canvasTag in self.drawingIDs:
            targetCanvas.delete(self.drawingIDs[canvasTag])
            del self.drawingIDs[canvasTag]
        for dv in self.decorations.values():
            if canvasTag in dv['drawingIDs']:
                targetCanvas.delete(dv['drawingIDs'][canvasTag])
                del dv['drawingIDs'][canvasTag]


    def deregisterCanvas(self,canvasTag):
        '''
            to deregister a rectangle from a given canvas, the latter's tag suffices
        '''
        assert (canvasTag in self.boundCanvases)

        self.unshowRectangle(canvasTag)

        self.boundCanvases=self.boundCanvases - {canvasTag}