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
    
    def __init__(self,p1,p2,canvasMap,color='red'):
        self.srcPoints=(p1.copy(),p2.copy())
        self.boundCanvases=set()
        self.canvasMap=canvasMap
        self.drawingIDs={}
        self.color=color

    def setColor(self,color='red'):
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

    def sortedTuple(self):
        '''
            returns a 4-item tuple of sorted (x_min,y_min,x_max,y_max) values for use with Canvas.create_rectangle
        '''
        return tuple([fun([pt[dim] for pt in self.srcPoints]) for fun in [min,max] for dim in ['x','y']])

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
        newPts[xindex].y=newPoint.y
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

    def unshowRectangle(self,canvasTag):
        targetCanvas=self.canvasMap[canvasTag] # is a sfCanvas
        if canvasTag in self.drawingIDs:
            targetCanvas.delete(self.drawingIDs[canvasTag])
            del self.drawingIDs[canvasTag]

    def deregisterCanvas(self,canvasTag):
        '''
            to deregister a rectangle from a given canvas, the latter's tag suffices
        '''
        assert (canvasTag in self.boundCanvases)

        self.unshowRectangle(canvasTag)

        self.boundCanvases=self.boundCanvases - {canvasTag}
