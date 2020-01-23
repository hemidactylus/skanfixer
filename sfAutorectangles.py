'''
    sfAutorectangles.py
        Library for automated image inspection
'''

from PIL import Image
import numpy as np
from time import time
from scipy import ndimage as nd

from sfPoint import sfPoint
from sfUtilities import popItem

def locateRectangles(image,erosionIterations=20,dilationIterations=10,
        minRectanglePixelFraction=None,whiteThreshold=None,
        shrinkFactor=1):
    '''
        Applies some basic morhpology to an image
        and returns a list of 2-tuples of sfPoints
        expressing the guessed no-overlap rectangles
        against a whiteish background.

        whiteThreshold can be 0-256 or None. None=auto detect
        minRectanglePixelSize = None implies 0.04 of the original size

        shrinkFactor > 1 means that sf^2 pixels are made into a single one,
        for a sf^2 speed improvement and a sf precision (linear) loss

    '''
    # convert to grayscale, no alpha channel
    orig_greyimage=image.convert('L')
    # apply shrinkFactor if required
    origShape=orig_greyimage.size
    if shrinkFactor>1:
        _newX=int(origShape[0]/float(shrinkFactor))
        _newY=int(origShape[1]/float(shrinkFactor))
        greyimage=orig_greyimage.resize((_newX,_newY),Image.ANTIALIAS)
    else:
        greyimage=orig_greyimage
    imdata_orig=np.asarray(greyimage)
    # if required, determine automatically the white-cut threshold
    if whiteThreshold is None:
        whiteThreshold = find_background_luminance(imdata_orig)
    #
    imdata=imdata_orig<whiteThreshold
    # try some erosion/dilation to refine clusters
    eroded=nd.binary_erosion(imdata,iterations=erosionIterations) # TEMP

    # back to an image
    resimage=Image.fromarray(np.uint8(eroded.astype(int)*255))

    dilated=nd.binary_dilation(eroded,iterations=dilationIterations)
    # back to an image
    resimage=Image.fromarray(np.uint8(dilated.astype(int)*255))

    # try and find regions
    laberoded,labels=nd.label(dilated)
    totlen=laberoded.shape[0]*laberoded.shape[1]
    lineroded=laberoded.reshape(totlen)
    labelsizes=np.bincount(lineroded)
    # labelsizes contains the (index,size) of each of the non-background components. Apply a cut here if desired
    if minRectanglePixelFraction is None:
        minRectanglePixelFraction = 0.04
    minRectanglePixelSize=int(minRectanglePixelFraction * totlen)
    regions=[]
    for rlabel in range(1,labels+1):
        if labelsizes[rlabel] >= minRectanglePixelSize:
            # find extrema of this region with a trick
            theseXs=np.where(np.any(laberoded==rlabel,axis=0))[0]
            theseYs=np.where(np.any(laberoded==rlabel,axis=1))[0]
            xmin=theseXs[0]
            xmax=theseXs[-1]
            ymin=theseYs[0]
            ymax=theseYs[-1]
            regions.append((sfPoint(xmin,ymin),sfPoint(xmax,ymax)))

    # here each rectangle is added/merged onto a stack so that if
    # a new rectangle to insert has some overlap to an existing one they become a larger rectangle.
    # This has to be iterated until there are no merging anymore.
    # Performance is no big deal (there aren't many rectangles at this point), but there has to be
    # a more elegant and less wasting solution

    startRegions=regions
    mergedRegions=[]
    while True:
        mergedRegions=merge_rectangles(startRegions)
        if len(mergedRegions)==len(startRegions):
            break
        startRegions=mergedRegions

    if shrinkFactor>1:
        # re-correct for the actual rectangle size
        # _newX=int(orig_greyimage.shape[0]/float(shrinkFactor))
        # _newY=int(orig_greyimage.shape[1]/float(shrinkFactor))
        finalRegions=[]
        limvalX=(0,origShape[0])
        limvalY=(0,origShape[1])
        shft=((-0.5,-0.5),(0.5,0.5))
        for qRe in mergedRegions:
            nRe=tuple(sp.shift(*sh).rescale(shrinkFactor,shrinkFactor,limvalX,limvalY) for sp,sh in zip(qRe,shft))
            finalRegions.append(nRe)
    else:
        finalRegions=mergedRegions

    return finalRegions

def find_background_luminance(npImage):
    '''
        Inspects the greyscale histogram to locate a meaningful threshold signaling
        background color

        Once the histogram is known, it is multiplied by a damping-factor
        function which is:
            zero                in    0 ... BLACKEND
            growing ^2 to one   in  BLACKEND ... WHITEBEGIN
            one                 in  WHITEBEGIN ... 255
        Then the first bar that is at 95% of the max is taken as the max

    '''
    BLACKEND=210
    WHITEBEGIN=240

    totlen=npImage.shape[0]*npImage.shape[1]
    imdata_lin=npImage.reshape(totlen)
    _y,_x=np.histogram(imdata_lin,range=(0,255),bins=255)
    _x=_x[:len(_y)]

    damping=np.zeros(len(_y),np.float)
    damping[WHITEBEGIN:]=1.0
    damping[BLACKEND:WHITEBEGIN]=np.linspace(0,1,WHITEBEGIN-BLACKEND)**2
    _wy=_y*damping

    # we get as bgcolor the first grey (from black to white) which
    # has a histogram bar >= 1% of the total number of pixels.
    absThreshold=int(0.01*np.max(_wy))
    if any(_wy>absThreshold):
        _maxind=np.argmax(_wy>absThreshold)
    else:
        # If greys are so evenly distributed that the above fails,
        # return the absolute maximum within the damped array
        _maxind=np.argmax(_wy)
    if _maxind>4:
        _maxind-=4
    else:
        _maxind=0
    return int(_x[_maxind])

def merge_rectangles(srcRegions):
    '''

        Given an input list of 2-uples containing sfPoints which are the left-top-most and the right-bottom-most
        corner of a rectangle each, it reduces their number by merging any two who happend to overlap.
        The merge is done onto the smallest rectangle containing both.

        To Be Implemented
    '''

    dstRegions=[]
    for newRegion in srcRegions:
        # if it has no overlap with any already-added region, proceed.
        # Otherwise replace the latter with the merge
        mrgRegion=None
        for chkRegion in dstRegions:
            mrgRegion=determine_overlap(chkRegion,newRegion)
            if mrgRegion:
                break
        if mrgRegion is not None:
            popItem(dstRegions,chkRegion)
            dstRegions.append(mrgRegion)
        else:
            dstRegions.append(newRegion)
    return dstRegions

def determine_overlap(recta1,recta2):
    '''
        Given two rectangles as a 2-tuple of sfPoints each, they are
        checked for overlap. In case of no overlap, None is returned, otherwise
        a new rectangle (2-uple of sfPoints) is generated, the minimal one
        containing both input objects.

        It is *assumed* that the NW corner is the first element of the tuple
        and the SE is the second.

    '''
    # various non-overlap relative positionings

    if recta1[1].x <= recta2[0].x:
        return None
    elif recta1[1].y <= recta2[0].y:
        return None
    elif recta1[0].x >= recta2[1].x:
        return None
    elif recta1[0].y >= recta2[1].y:
        return None
    else:
        # now there is an overlap and a merge is performed
        return (
                    sfPoint(min(recta1[0].x,recta2[0].x),min(recta1[0].y,recta2[0].y)),
                    sfPoint(max(recta1[1].x,recta2[1].x),max(recta1[1].y,recta2[1].y)),
                )

if __name__=='__main__':
    print('Testing')
    #
    pic=Image.open('/home/stefano/temp/NotBackedUp/PicsForSkanfixer/p0035.jpg')
    _ini=time()
    for i,r in  enumerate(locateRectangles(pic)):
        print('  ',i, r)
    print('Done in %f' % (time()-_ini))
    #
    print('Done')
