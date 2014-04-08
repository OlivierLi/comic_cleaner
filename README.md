ComicCleaner
============
Scanning your own comic collection for safekeeping is fun. Corrupted or incomplete archives are not! 
comicCleaner analyzes your comic library and finds all the broken and incomplete {*cbr,cbz*} files.

## How it works:

When ComicCleaner is run without the <code>--clean</code> option it will simply scan your library and report broken comics. Comics that have no or too few pages will also be reported as they indicate an incomplete scan. 

When run with the <code>--clean</code> option Comiccleaner will start the execution by scanning the directory indicated by <code>banned_files_dir</code> and calculate the checksums of the files it contains. An example of a page that could be remove this way is a personal cover you added to your scans and no longer want.

ComicCleaner then scans your library again and when it encounters one of these banned files it will remove it from the comic. The new comic will be saved using the *cbz* format and the old comic will be backed up with a *.bak* extension.

## Usage:

**./comicCleaner.py** [-h] [--clean] [--banned_files_dir BANNED_FILES_DIR] [--dry_run] library_path

**library_path**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The location of your library  
**-h, --help**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Show this help message and exit  
**--clean**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Remove banned files from the comics  
**--banned_files_dir BANNED_FILES_DIR**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The directory contaning the banned files.  
**--dry_run**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Display information only. No file will be modified

## Dependencies:
ComicCleaner uses  [rarfile](https://pypi.python.org/pypi/rarfile/2.2).  
You can install it using : <code>sudo pip install rarfile</code>

###Disclaimer : 
ComicCleaner is for use with comics you scanned yourself or acquired by legal means. I do not condone piracy in any way.
