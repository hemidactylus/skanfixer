# sfUtilities: general utilities
import os

def popItem(qList,qItem):
    qList.pop(qList.index(qItem))
    return

# file- and image-related utilities
def listImageFiles(nDir):
    '''
        Builds a list of image files for a given directory
    '''
    return [fN for fN in os.listdir(nDir) if isPicture(fN)]

def isPicture(filename):
    '''
        temporary implementation: this returns True for files which are image files
    '''
    return filename[-3:].lower() in ['jpg'] or filename[-4:].lower() in ['jpeg']
