'''
    sfAffineMaps module: creates and handles affine maps from cartesian plane to cartesian plane.
        Those are functions from (sfPoint,'d') to sfPoint for the direct map (from object to external coordinates)
        and from (sfPoint, 'r') to sfPoint for the reversed map (external to object coordinates)
'''

from sfPoint import sfPoint

# temp version
def createAffineMap(fucktor=2):
    _f=float(fucktor)
    def mapper(qpoint, mode='d'):
        if mode=='d':
            return sfPoint(qpoint.x*_f,qpoint.y*_f)
        elif mode=='r':
            return sfPoint(qpoint.x/_f,qpoint.y/_f)
        else:
            raise ValueError('mode')

    return mapper
