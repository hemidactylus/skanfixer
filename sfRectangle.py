'''
    Class sfRectangle for multi-rectangle selection.
    Features a multiple map to canvases, each with its own affine map from the real coordinates
    to the ones for the canvas.
'''

import tkinter as tk
from PIL import Image

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

# constant-side-index (w.r.t. sortedTuple) for rotation marker
ST_IND_SEQ=(3,2,1,0)
'''
    This means: rotation index 2 -> third item=1 -> ymin is the constant, hence the varying is x*
'''

TRANSPOSE_PARAMETER_VALUES=[
    0,
    Image.ROTATE_270,
    Image.ROTATE_180,
    Image.ROTATE_90,
]

class sfRectangle():
    
    def __init__(self,p1,p2,canvasMap,color='red'):
        self.srcPoints=(p1.copy(),p2.copy())
        self.boundCanvases=set()
        self.canvasMap=canvasMap
        self.drawingIDs={}
        self.color=color
        self.decorations={}
        self.setLabel(None)
        self.setRotation(0)

    def setRotation(self,rotation):
        self.rotation=rotation # 0=bottom, 1=right, 2=top, 3=left: marks the side which will be doubly-marked
        self.undecorate('rotation')
        self.decorate('rotation','r',rotation)

    def rotateTransposeParameter(self):
        '''
            returns the parameter to feed Image.transpose in order to achieve
            the rotation angle corresponding to the rectangle's rotation value
        '''
        return TRANSPOSE_PARAMETER_VALUES[self.rotation]

    def setColor(self,color='red'):
        if self.color!=color:
            self.color=color
            self.refreshDisplay()

    def relimit(self,pt1,pt2):
        '''
            Constrain all coordinates to lie within the range defined by the two arena-delimiting
            point (ends included)
        '''
        _changed=False
        for pt in self.srcPoints:
            for qdim in ['x','y']:
                _minVal=min([spt[qdim] for spt in [pt1,pt2]])
                _maxVal=max([spt[qdim] for spt in [pt1,pt2]])
                if pt[qdim] < _minVal:
                    pt[qdim]=_minVal
                    _changed=True
                if pt[qdim] > _maxVal:
                    _changed=True
                    pt[qdim]=_maxVal
        if _changed:
            self.refreshDisplay()

    def __str__(self):
        return 'sfRectangle{%s ; %s}' % (self.srcPoints)

    def description(self):
        '''
            returns a status-bar-friendly rectangle descriptive text
        '''
        _st=self.sortedTuple()
        _w=int(_st[2]-_st[0])
        _h=int(_st[3]-_st[1])
        _l=' "%s"' % self.label if self.label else ''
        _r=float(_w)/float(_h) if _h>0 else 0
        _rot='DRUL'[self.rotation]
        return 'Rectangle%s (%i x %i px, AR=%.4f, rot=%s)' % (_l,_w,_h,_r,_rot)

    def setLabel(self,newLabel):
        self.label=newLabel
        # here attach handling of decoration, if any
        self.undecorate('labeling')
        if newLabel is not None:
            self.decorate('labeling','d',newLabel)

    def bareCopy(self):
        return sfRectangle(self.srcPoints[0],self.srcPoints[1],self.canvasMap)

    def corners(self):
        '''
            returns all four corners as a 4-item array of sfPoints,
            arranged in the order specified by XY_IND_SEQ
        '''
        return [sfPoint(self.srcPoints[ix]['x'],self.srcPoints[iy]['y'],) for ix,iy in XY_IND_SEQ]

    def nearestCorner(self,oPoint,mapper=None):
        '''
            returns a 2-uple (index,distance2) of the corner (out of four)
            which is closest to the provided point
        '''
        if mapper is None:
            mapper=createAffineMap()
        pDistances=[oPoint.distance2(corner,mapper) for corner in self.corners()]
        return sorted(enumerate(pDistances),key=lambda x: x[1])[0]

    def nearestMidpoint(self,oPoint,mapper=None):
        '''
            returns a 2-uple (index,distance2) of the midpoint (out of four, indexed
            as n -> between points n and (n+1)%4)
            which is closest to the provided point
        '''
        if mapper is None:
            mapper=createAffineMap()
        sCorners=list(self.corners())
        mDistances=[oPoint.distance2(corner1.midpoint(corner2),mapper)
            for corner1,corner2 in zip(sCorners,sCorners[1:]+sCorners[0:1])]
        return sorted(enumerate(mDistances),key=lambda x: x[1])[0]

    def anywhereDistance(self,oPoint,mapper=None):
        '''
            returns a 'distance to rectangle', defined as the min distance
            between any point on the rectangle outline and the given oPoint
        '''
        if mapper is None:
            mapper=createAffineMap()
        cCorners=list(self.corners())
        distances=[]
        for cSegment in zip(cCorners,cCorners[1:]+cCorners[0:1]):
            distances.append(oPoint.distanceToAxisSegment(cSegment,mapper))
        return min(distances)

    def sortedTuple(self,integer=False):
        '''
            returns a 4-item tuple of sorted (x_min,y_min,x_max,y_max) values for use with Canvas.create_rectangle
        '''
        if integer:
            return tuple([int(fun([pt[dim] for pt in self.srcPoints])) for fun in [min,max] for dim in ['x','y']])
        else:
            return tuple([fun([pt[dim] for pt in self.srcPoints]) for fun in [min,max] for dim in ['x','y']])

    def decorate(self,tag,decType,decIndex):
        '''
            adds a decoration - a graphical gizmo - to the representation of the rectangle.
            tag is used for subsequent undecoration
            decType='c' or 's' for corner or side resp.
            decIndex is a 0-3 index to specify decoration position, or something else for various decorations

            This call automatically triggers redisplay on all attached canvases
        '''
        if decType in ['c','s','r','d']:
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
        drawingID=targetCanvas.create_rectangle(mapRect.sortedTuple(),
                                                width=settings['RECTANGLE']['WIDTH'],
                                                outline=self.color,
                                            )
        self.drawingIDs[canvasTag]=drawingID
        # handle decorations attached to this rectangle
        for dk,dv in self.decorations.items():
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
        elif dType=='r':
            # use dIndex and ST_IND_SEQ to determine which side is the rotation-wise bottom side
            # *note* this is relative to the sortedTuple notation
            # Now the extremes of the segment to draw are calculated
            _sTuple=self.sortedTuple()
            flatDimInd=ST_IND_SEQ[dIndex]    # index of the dim common to the two points
            otherFlatDimInd=(2+flatDimInd)%4 # same orientation as the above, the other side (used for displacing)
            flatDimName='xy'[flatDimInd%2]   # either 'x' or 'y', associated to above
            varDimInd=[
                ind+(flatDimInd+1)%2
                for ind in (0,2)
            ]
                                             # this becomes 0,2 or 1,3, opposite to the flatDim
            varDimName='yx'[flatDimInd%2]    # either 'x' or 'y', associated both values above
            # building of the segment extremes
            flatDimValue=(lambda pfar,pnear: pfar+settings['RECTANGLE']['BOTTOMFRACTION']*(pnear-pfar))\
                (_sTuple[otherFlatDimInd],_sTuple[flatDimInd])
            segmentPoints=[coordMapper(sfPoint(**{
                    flatDimName: flatDimValue,
                    varDimName: _sTuple[varDimInd[pointindex]],
                }),'r') for pointindex in (0,1)]
            # print 'PT 0', coordMapper(segmentPoints[0],'d')
            # print 'PT 1', coordMapper(segmentPoints[1],'d')
            return tCanvas.create_line(
                                            segmentPoints[0].x,segmentPoints[0].y,
                                            segmentPoints[1].x,segmentPoints[1].y,
                                            width=settings['RECTANGLE']['BOTTOMWIDTH'],
                                            fill=self.color,
                                        )
        elif dType=='d':
            # print the label contained in dIndex on the rectangle
            _sTuple=self.sortedTuple()
            _lOrigin=coordMapper(sfPoint(x=_sTuple[0],y=_sTuple[3]),'r')
            return tCanvas.create_text(
                                            _lOrigin.x+8,_lOrigin.y-6,
                                            text=dIndex, stipple='gray25',
                                            fill=self.color, anchor=tk.SW,

                                        )
        else:
            raise ValueError

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
