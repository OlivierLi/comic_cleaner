#!/usr/bin/python

import sys
import os
import fnmatch
import rarfile
import zipfile
import re

def isCbrValid(comicPath):
       
    # If an exception is raised here it's probably an error with the file
    # TODO catch just apropriate exceptions just to be sure.
    try:
        rf = rarfile.RarFile(comicPath)
        pageNames = rf.namelist()
        numberOfFiles = len(pageNames)
    except:
        print comicPath + " is invalid because the archive is corrupted."
        return False
        
    # Assume a comic can't have less than 10 pages
    if(numberOfFiles < 15):
        print comicPath + " is invalid because it has too few pages."
        return False
    
    return True

# TODO It's possible that all non-numbered pages are scene garbage. Check that out
# TODO Find out if nameList() gives all the file names even if they are in folders
        
def isCbzValid(comicPath):
    try:
        zf = zipfile.ZipFile(comicPath)
        pageNames = zf.namelist()
        numberOfFiles=len(pageNames)

    except:
        print comic + " is invalid because the archive is corrupted."
        return False
    
    # Assume a comic can't have less than 10 pages
    if(numberOfFiles < 15):
        print comic + " is invalid because it has too few pages."
        return False
    
    return True

def main():
    
    if (len(sys.argv) < 2):
        print "You must provide a directory to look into!"
        sys.exit(-1)

    directory = sys.argv[1]

    if (not os.path.isdir(directory) or not os.path.exists(directory)):
        print "You must provide a valid directory to look into!"
        sys.exit(-1)

    # First lets recursively find all the comics in the library 
    comics = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, '*.cb?'):
            comics.append(os.path.join(root, filename))
    
    # Loop over all comics and simply find the corrupted ones.
    # Corrupted comics are removed from the list
    for comic in comics:
        if fnmatch.fnmatchcase(comic, "*.cbz"):
            if not isCbzValid(comic):
                comics.remove(comic)
                
        elif fnmatch.fnmatchcase(comic, "*.cbr"):
            if not isCbrValid(comic):
                comics.remove(comic)

    # Even if the archive is valid the last pages might be missing which is hard to detect without knowing how many pages comics of the series usually have.
    # If not corrupted then compute the average number of pages for each subdirectory
    # Then for each directory look at each comic. If the number is 3 pages smaller than the average, notify.

    # TODO Create a list of known ads/unwanted pictures. Then when scanning, check the name of the files for the offending titles
    # to warn if one of these pages is found in the comics.
    # TODO Possibly find opencv to find logos which indicate full page ads

if __name__ == "__main__":
        main()
