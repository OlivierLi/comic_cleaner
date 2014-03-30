#!/usr/bin/python3

import sys
import os
import fnmatch
import rarfile
import zipfile


def is_cbr_valid(comic_path):
    # If an exception is raised here it's probably an error with the file
    try:
        rf = rarfile.RarFile(comic_path)
        page_info_list = rf.infolist()

        number_of_files = 0

        if len(page_info_list) > 0:
            cover_size = page_info_list[0].file_size

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


if __name__ == "__main__":
    main()
