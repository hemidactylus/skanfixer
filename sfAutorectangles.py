'''
    sfAutorectangles.py
        Library for automated image inspection
'''

from PIL import Image
import numpy as np
from time import time
from scipy import ndimage as nd

from sfPoint import sfPoint

def handleImage(image):
    # (resize and) convert to grayscale, no alpha channel
    greyimage=image.resize((300,420),Image.ANTIALIAS).convert('L')
    # image2.save('a.jpg','jpeg')
    imdata_orig=np.asarray(greyimage)
    imdata=255-imdata_orig
    imdata=imdata>10
    # try some erosion
    eroded=nd.binary_erosion(imdata,iterations=5)
    # eroded=nd.grey_erosion(imdata,(10,10),mode='constant')
    # back to an image
    resimage=Image.fromarray(np.uint8(eroded.astype(int)*255))
    # resimage=Image.fromarray(eroded)
    resimage.save('a.jpg','jpeg')
    # try and find regions

    laberoded,labels=nd.label(eroded)
    totlen=laberoded.shape[0]*laberoded.shape[1]
    lineroded=laberoded.reshape(totlen)
    labelsizes=np.bincount(lineroded)
    # labelsizes contains the (index,size) of each of the non-background components. Apply a cut here if desired
    MIN_LABEL_SIZE=1000
    print 'RESULT: %s' % (labelsizes)
    print 'Labels: ', labels
    regions=[]
    for rlabel in range(1,labels+1):
        print 'LAB ', rlabel
        if labelsizes[rlabel] >= MIN_LABEL_SIZE:
            # find extrema of this region with a trick
            theseXs=np.where(np.any(laberoded==rlabel,axis=0))[0]
            theseYs=np.where(np.any(laberoded==rlabel,axis=1))[0]
            xmin=theseXs[0]
            xmax=theseXs[-1]
            ymin=theseYs[0]
            ymax=theseYs[-1]
            print 'Label %i => (%i,%i) to (%i,%i)' % (rlabel,xmin,ymin,xmax,ymax)
            regions.append((sfPoint(xmin,ymin),sfPoint(xmax,ymax)))

    # SIMULATE SOMETHING TO DO
    regions.append((sfPoint(150,320),sfPoint(214,413))) # this overlaps with the last real one

    print 'REGIONS BEFORE OVERLAP CHECK:\n', '\n'.join('    %s ==> %s' % reg for reg in regions)

    # here each rectangle is added/merged onto a stack so that if
    # a new rectangle to insert has some overlap to an existing one they become a larger rectangle.
    # This has to be iterated until there are no merging anymore.
    # Performance is no big deal (there aren't many rectangles at this point), but there has to be
    # a more elegant and less wasting solution
    startRegions=regions
    mergedRegions=[]
    while len(startRegions)!=len(mergedRegions):
        startRegions=mergedRegions
        mergedRegions=merge_rectangles(mergedRegions)

    print 'REGIONS AFTER MERGING:\n', '\n'.join('    %s ==> %s' % reg for reg in regions)

def merge_rectangles(srcRegions):
    '''

        Given an input list of 2-uples containing sfPoints which are the left-top-most and the right-bottom-most
        corner of a rectangle each, it reduces their number by merging any two who happend to overlap.
        The merge is done onto the smallest rectangle containing both.

        To Be Implemented
    '''
    raise NotImplementedError
    return srcRegions

if __name__=='__main__':
    print 'Testing'
    #
    pic=Image.open('/home/stefano/temp/NotBackedUp/PicsForSkanfixer/p0035.jpg')
    _ini=time()
    handleImage(pic)
    print 'Done in %f' % (time()-_ini)
    #
    print 'Done'
