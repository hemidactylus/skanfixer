'''
    sfAffineMaps module: creates and handles affine maps from cartesian plane to cartesian plane.
        Those are functions from (sfPoint,'d') to sfPoint for the direct map (from object to external coordinates)
        and from (sfPoint, 'r') to sfPoint for the reversed map (external to object coordinates)
        (Note: 'external'=the real ones, unique. 'object'=their conversion to a disposable canvas - one of many canvases in principle)
'''

from sfPoint import sfPoint

# temp version
def createAffineMap(factorX=1.0, factorY=1.0, deltaX=0.0, deltaY=0.0):
    _fx=float(factorX)
    _fy=float(factorY)
    _dx=float(deltaX)
    _dy=float(deltaY)
    def mapper(qpoint, mode='d'):
        if mode=='d':
            return sfPoint(qpoint.x*_fx+_dx,qpoint.y*_fy+_dy)
        elif mode=='r':
            return sfPoint((qpoint.x-_dx)/_fx,(qpoint.y-_dy)/_fy)
        else:
            raise ValueError('mode')

    return mapper
