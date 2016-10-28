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

def locateRectangles(image,erodilateIterations=5,minRectanglePixelSize=5000,whiteThreshold=None):
    '''
        Applies some basic morhpology to an image
        and returns a list of 2-tuples of sfPoints
        expressing the guessed no-overlap rectangles
        against a whiteish background.
    '''
    # convert to grayscale, no alpha channel
    greyimage=image.convert('L')
    # greyimage=image.resize((300,420),Image.ANTIALIAS).convert('L')
    # greyimage.save('a.jpg','jpeg')
    imdata_orig=np.asarray(greyimage)
    # if required, determine automatically the white-cut threshold
    if whiteThreshold is None:
        whiteThreshold = find_background_luminance(imdata_orig)
    #
    imdata=imdata_orig<whiteThreshold
    # try some erosion/dilation to refine clusters
    eroded=nd.binary_erosion(imdata,iterations=erodilateIterations)
    dilated=nd.binary_dilation(eroded,iterations=erodilateIterations)
    # back to an image
    resimage=Image.fromarray(np.uint8(dilated.astype(int)*255))
    # resimage.save('b.jpg','jpeg')

    # try and find regions
    laberoded,labels=nd.label(dilated)
    totlen=laberoded.shape[0]*laberoded.shape[1]
    lineroded=laberoded.reshape(totlen)
    labelsizes=np.bincount(lineroded)
    # labelsizes contains the (index,size) of each of the non-background components. Apply a cut here if desired
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

    return mergedRegions

def find_background_luminance(npImage):
    '''
        Inspects the greyscale histogram to locate a meaningful threshold signaling
        background color
    '''
    return 245

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
    print 'Testing'
    #
    pic=Image.open('/home/stefano/temp/NotBackedUp/PicsForSkanfixer/p0035.jpg')
    _ini=time()
    for i,r in  enumerate(locateRectangles(pic)):
        print '  ',i, r
    print 'Done in %f' % (time()-_ini)
    #
    print 'Done'
