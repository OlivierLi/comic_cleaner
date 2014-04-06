#!/usr/bin/python3

import sys
import os
import fnmatch
import rarfile
import zipfile
import binascii

#When a file with this crc is encountered it will be removed from the archive
banned_crcs = []


def crc32_from_file(filename):
    buffer = open(filename, 'rb').read()
    crc_value = binascii.crc32(buffer)
    return crc_value


def gather_crcs(directory):

    if not os.path.isdir(directory) or not os.path.exists(directory):
        print("The ad directory is invalid!")
        sys.exit(-1)

    crcs = []

    for dirpath, dirnames, filenames in os.walk(directory):
        for filneame in filenames:
            full_path = os.path.abspath(os.path.join(dirpath, filneame))
            crcs.append(crc32_from_file(full_path))

    return crcs


def clean_cbr(comic_path):

    global banned_crcs

    rf = rarfile.RarFile(comic_path)
    page_info_list = rf.infolist()

    for info in page_info_list:
        for banned_crc in banned_crcs:
            if info.CRC == banned_crc:
                print("Banned page found in :" + comic_path)


def is_cbr_valid(comic_path):
    # If an exception is raised here it's probably an error with the file
    try:
        rf = rarfile.RarFile(comic_path)
        page_info_list = rf.infolist()

        number_of_files = 0

        if len(page_info_list) > 0:
            cover_size = page_info_list[0].file_size
        else:
            return False

        #See if each page is a single or double page based on the size
        for info in page_info_list:
            if info.file_size < cover_size * 1.5:
                number_of_files += 1
            else:
                number_of_files += 2

    except rarfile.BadRarFile:
        print(comic_path + " is invalid because the archive is corrupted.")
        return False

    # Assume a comic can't have less than 15 pages
    if number_of_files < 15:
        print(comic_path + " is invalid because it has too few pages.")
        return False

    return True


# TODO It's possible that all non-numbered pages are scene garbage. Check that out
# TODO Find out if nameList() gives all the file names even if they are in folders

def is_cbz_valid(comic_path):
    try:
        zf = zipfile.ZipFile(comic_path)
        page_info_list = zf.infolist()
        number_of_files = 0

        if len(page_info_list) > 0:
            cover_size = page_info_list[0].file_size
        else:
            return False

        #See if each page is a single or double page based on the size
        for info in page_info_list:
            if info.file_size < cover_size * 1.5:
                number_of_files += 1
            else:
                number_of_files += 2

    except zipfile.BadZipfile:
        print(comic_path + " is invalid because the archive is corrupted.")
        return False

    # Assume a comic can't have less than 15 pages
    if number_of_files < 15:
        print(comic_path + " is invalid because it has too few pages.")
        return False

    return True


def main():
    if len(sys.argv) < 2:
        print("You must provide a directory to look into!")
        sys.exit(-1)

    directory = sys.argv[1]

    if not os.path.isdir(directory) or not os.path.exists(directory):
        print("You must provide a valid directory to look into!")
        sys.exit(-1)

    #Lets find the crcs of the banned images
    global banned_crcs
    banned_crcs = gather_crcs("pages_to_remove")

    # First lets recursively find all the comics in the library 
    comics = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, '*.cb?'):
            comics.append(os.path.join(root, filename))

    # Loop over all comics and simply find the corrupted ones.
    # Corrupted comics are removed from the list
    for comic in comics:
        if fnmatch.fnmatchcase(comic, "*.cbz"):
            if not is_cbz_valid(comic):
                comics.remove(comic)

        elif fnmatch.fnmatchcase(comic, "*.cbr"):
            if not is_cbr_valid(comic):
                comics.remove(comic)

    #Now that invalid archive are excluded we can proceed with cleaning them
    for comic in comics:
        if fnmatch.fnmatchcase(comic, "*.cbz"):
            #TODO add cleaning function for cbzs
            pass

        elif fnmatch.fnmatchcase(comic, "*.cbr"):
            clean_cbr(comic)


if __name__ == "__main__":
    main()
