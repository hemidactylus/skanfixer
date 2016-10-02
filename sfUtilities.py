# sfUtilities: general utilities
import os

PIC_SUFFIXES=['jpg','jpeg','bmp','tiff','gif','png']

def popItem(qList,qItem):
    qList.pop(qList.index(qItem))
    return

# file- and image-related utilities
def listImageFiles(nDir):
    '''
        Builds a list of image files for a given directory
    '''
    return sorted([fN for fN in os.listdir(nDir) if isPicture(fN)])

def isPicture(filename):
    '''
        temporary implementation: this returns True for files which are image files
    '''
    return any(filename[-len(suffix):] == suffix for suffix in PIC_SUFFIXES)

def findRescaleFactor(imgSize,allowedSize,allowZoom=True):
    '''
        finds the rescale factor given an image size and the size of the container
    '''
    mFactor=max(float(imgDim)/float(alwDim) for imgDim,alwDim in zip(imgSize,allowedSize))
    if not allowZoom:
        if mFactor<1:
            mFactor=1
    print 'mFactor=%.3f' % mFactor
    return mFactor

fileNameAllowedChars='qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'+\
                     '1234567890-_~.,'
def normalizeString(inText):
    '''
        Very strictly discards all characters not falling within a specified
        set of allowed ones. Used to store labels as filename parts
    '''
    return ''.join([c for c in inText if c in fileNameAllowedChars])
