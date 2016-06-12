'''
    miscUtils : miscellaneous utilities for skanfixer
'''

# standard imports
import os

DEBUG=True

def isPicture(filename):
    '''
        temporary implementation: this returns True for files which are image files
    '''
    return filename[-3:].lower() == 'jpg' or filename[-4:].lower() == 'jpeg'

def findRescaleFactor(imgSize,allowedSize,allowZoom=True):
    '''
        finds the rescale factor given an image size and the size of the container
    '''
    mFactor=min(float(alwDim)/float(imgDim) for imgDim,alwDim in zip(imgSize,allowedSize))
    if not allowZoom:
        if mFactor>1:
            mFactor=1
    if DEBUG:
        print 'mFactor=%.3f' % mFactor
    return mFactor

def listImageFiles(nDir):
    '''
        Builds a list of image files for a given directory
    '''
    return [fN for fN in os.listdir(nDir) if isPicture(fN)]

def centreAroundPoint(pos,size):
    '''
        given a (x,y) position and a (dx,dy) size, returns
        the coordinate of the top-left corner were the
        size to be centred at the position
    '''
    return tuple(p-s/2 for p,s in zip(pos,size))

def mapCoordinatesFromZoom(coordsOnZoom,zoomWindowCenter, picZoomShape, zFactor, showFactor):
    '''
    todo: from a coordinate on the zoom window to coordinates in the original picture!
    '''