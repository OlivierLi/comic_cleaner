#!/usr/bin/python3

import sys
import os
import fnmatch
import rarfile
import zipfile
import binascii
import shutil
import argparse

#When a file with this crc is encountered it will be removed from the archive
banned_crcs = []

#If dry_run is selected then no files will be modified
dry_run = False


#Go over the directory and gather the crcs of the files inside
def gather_crcs(directory):
    if not os.path.isdir(directory) or not os.path.exists(directory):
        print("The ad directory is invalid!")
        sys.exit(-1)

    crcs = []

    for dirpath, dirnames, filenames in os.walk(directory):
        for filneame in filenames:
            full_path = os.path.abspath(os.path.join(dirpath, filneame))

            buffer = open(full_path, 'rb').read()
            crc_value = binascii.crc32(buffer)

            crcs.append(crc_value)

    return crcs


#Go over the archive and find out if some of its file are banned
#If there are banned files remove them from the archive
def clean_cbr(comic_path):
    global banned_crcs
    global dry_run

    rar_file_in = rarfile.RarFile(comic_path)
    page_info_list = rar_file_in.infolist()

    #The crcs of all the files that have to be removed from the archive
    crcs_to_remove = []

    #Go over the file and find out if files have to be removed
    for info in page_info_list:
        for banned_crc in banned_crcs:
            if info.CRC == banned_crc:
                crcs_to_remove.append(info.CRC)
                print("Banned page (based on its CRC) found in :" + comic_path)

    #We are running a dry run so don't modify any files!
    if dry_run:
        return

    #Some files have to be removed
    if len(crcs_to_remove) > 0:

        #Create a backup of the file
        new_path = comic_path.replace("cbr", "bak")
        shutil.move(comic_path, new_path)

        #Recreate the rar file from the new path
        rar_file_in = rarfile.RarFile(new_path)
        page_info_list = rar_file_in.infolist()

        zip_file_out = zipfile.ZipFile(comic_path.replace("cbr", "cbz"), 'w')

        for info in page_info_list:
            if not info.isdir():
                buffer = rar_file_in.read(info.filename)
                if info.CRC not in crcs_to_remove:
                    zip_file_out.writestr(info.filename, buffer)


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

    except (rarfile.RarCRCError, rarfile.BadRarFile):
        print(comic_path + " is invalid because the archive is corrupted.")
        return False

    except rarfile.NotRarFile:
        print(comic_path + " is not a rar file. Maybe rename its a zip!")
        return False

    # Assume a comic can't have less than 15 pages
    if number_of_files < 15:
        print(comic_path + " is invalid because it has too few pages.")
        return False

    return True


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
    #Wether or not to clean the library
    do_clean = False

    parser = argparse.ArgumentParser(description="ComicCleaner cleans your comic library for you.")
    parser.add_argument('--directory', help='The location of your library', required=True)
    parser.add_argument('--clean', help='Wether the comics will be cleaned or not', action='store_true')
    parser.add_argument('--dry_run', help='Inform me that comics contain banned files but don\'t modify anything', action='store_true')
    args = vars(parser.parse_args())

    #The library will be cleaned
    if args['clean']:
        do_clean = True

    global dry_run
    dry_run = args['dry_run']

    if not os.path.isdir(args['directory']) or not os.path.exists(args['directory']):
        print("You must provide a valid directory to look into!")
        sys.exit(-1)

    #Lets find the crcs of the banned images
    global banned_crcs
    banned_crcs = gather_crcs("pages_to_remove")

    # First lets recursively find all the comics in the library 
    comics = []
    for root, dirnames, filenames in os.walk(args['directory']):
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

    #There is no cleaning up to, bail out
    if not do_clean and not dry_run:
        return

    #Now that invalid archive are excluded we can proceed with cleaning them
    for comic in comics:
        if fnmatch.fnmatchcase(comic, "*.cbz"):
            #TODO add cleaning function for cbzs
            pass

        elif fnmatch.fnmatchcase(comic, "*.cbr"):
            clean_cbr(comic)


if __name__ == "__main__":
    main()