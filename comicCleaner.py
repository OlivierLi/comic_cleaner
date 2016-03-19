#!/usr/bin/python3 
import sys
import os
import fnmatch
import rarfile
import zipfile
import binascii
import shutil
import argparse


# Go over the directory and gather the crcs of the files inside
def _gather_crcs(directory):
    if not os.path.isdir(directory) or not os.path.exists(directory):
        print("The ad directory is invalid!")
        sys.exit(-1)

    crcs = []

    for dirpath, dirnames, filenames in os.walk(directory):
        for filneame in filenames:
            full_path = os.path.abspath(os.path.join(dirpath, filneame))

            my_buffer = open(full_path, "rb").read()
            crc_value = binascii.crc32(my_buffer)

            crcs.append(crc_value)

    return crcs


# Go over the archive and find out if some of its file are banned
# If there are banned files remove them from the archive
def clean_comic(comic_path, banned_crcs, dry_run):
    if fnmatch.fnmatchcase(comic_path, "*.cbz"):
        archive = zipfile.ZipFile(comic_path)
    elif fnmatch.fnmatchcase(comic_path, "*.cbr"):
        archive = rarfile.RarFile(comic_path)
    else:
        print(comic_path + " is in an unsupported format!")
        return

    page_info_list = archive.infolist()

    # The crcs of all the files that have to be removed from the archive
    crcs_to_remove = []

    # Go over the file and find out if files have to be removed
    for info in page_info_list:
        for banned_crc in banned_crcs:
            if info.CRC == banned_crc:
                crcs_to_remove.append(info.CRC)
                print("Banned page (based on its CRC) found in :" + comic_path)

    # We are running a dry run so don"t modify any files!
    if dry_run:
        return

    # Some files have to be removed
    if len(crcs_to_remove) > 0:

        # Create a backup of the file
        new_path = comic_path[0:-3] + "bak"
        shutil.move(comic_path, new_path)

        # Recreate the rar file from the new path
        if fnmatch.fnmatchcase(comic_path, "*.cbz"):
            archive = zipfile.ZipFile(new_path)
        elif fnmatch.fnmatchcase(comic_path, "*.cbr"):
            archive = rarfile.RarFile(new_path)

        page_info_list = archive.infolist()

        # Only the creation of zips is supported
        zip_file_out = zipfile.ZipFile(comic_path[0:-3] + "cbz", "w")

        # Only rar files have a problem with extracting a directory
        for info in page_info_list:
            if isinstance(info, rarfile.RarInfo) and info.isdir():
                pass
            else:
                my_buffer = archive.read(info.filename)
                if info.CRC not in crcs_to_remove:
                    zip_file_out.writestr(info.filename, my_buffer)


def is_comic_valid(comic_path):
    # If an exception is raised here it"s probably an error with the file
    try:

        if fnmatch.fnmatchcase(comic_path, "*.cbz"):
            archive = zipfile.ZipFile(comic_path)
        elif fnmatch.fnmatchcase(comic_path, "*.cbr"):
            archive = rarfile.RarFile(comic_path)

        page_info_list = archive.infolist()

        number_of_files = 0

        if len(page_info_list) > 0:
            cover_size = page_info_list[0].file_size
        else:
            print(comic_path + " is invalid because it has no pages.")
            return False

        # See if each page is a single or double page based on the size
        for info in page_info_list:
            if info.file_size < cover_size * 1.5:
                number_of_files += 1
            else:
                number_of_files += 2

    except (zipfile.BadZipfile, rarfile.RarCRCError, rarfile.BadRarFile):
        print(comic_path + " is invalid because the archive is corrupted.")
        return False

    except rarfile.NotRarFile:
        print(comic_path + " is not a rar file. Maybe its a zip!")
        return False

    # Assume a comic can"t have less than 15 pages
    if number_of_files < 15:
        print(comic_path + " is invalid because it has too few pages.")
        return False

    return True


def clean_library(library_path, banned_files_dir=None, dry_run=True ):
    # First lets recursively find all the comics in the library
    comics = []

    for root, dirnames, filenames in os.walk(library_path):
        for filename in fnmatch.filter(filenames, "*.cb?"):
            comics.append(os.path.join(root, filename))

    # Loop over all comics and remove the corrupted ones from the list
    for comic in comics:
        if not is_comic_valid(comic):
            comics.remove(comic)

    # There is no cleaning up to, bail out
    if banned_files_dir:

        # Lets find the crcs of the banned images
        banned_crcs = _gather_crcs(banned_files_dir)

        for comic in comics:
            clean_comic(comic, banned_crcs, dry_run)


def main():
    parser = argparse.ArgumentParser(description="ComicCleaner cleans your comic library for you.")
    parser.add_argument("library_path", help="The location of your library")
    parser.add_argument("--banned_files_dir", help="The directory containing the banned files.")
    parser.add_argument("--dry_run", help="Display information only. No file will be modified", action="store_true")
    args = vars(parser.parse_args())

    if not os.path.isdir(args["library_path"]) or not os.path.exists(args["library_path"]):
        print("You must provide a valid directory to look into!")
        sys.exit(-1)

    clean_library(args["library_path"], args["banned_files_dir"], args["dry_run"])


if __name__ == "__main__":
    main()
