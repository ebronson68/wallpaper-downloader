#!./venv/bin/python3

import os
import getpass
import re
import requests
import tqdm
import time
import urllib
import json
from re import search
import argparse
from vars_file import api_key

now = time.time()

home_dir = os.getenv('HOME') + "/"
backgrounds_dir = home_dir + "Pictures/Backgrounds/"
downloaded_dir = backgrounds_dir + "Downloaded Backgrounds/"

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-v', '--verbose', action='count', help='increase the verbosity', default=0)
parser.add_argument('-d', '--directory', help='directory to save images to', default=downloaded_dir)
parser.add_argument('--min-width', help='min width of screen', default=1920, dest="min_width", type=int)
parser.add_argument('--min-height', help='min height of screen', default=1080, dest="min_height", type=int)
parser.add_argument('--force-aspect-ratio', help='only download files that match given aspect ratio', default='16x9', dest="force_aspect_ratio", choices=['25x16','3x2','5x4', '4x3', '16x10', '9x16', '16x9'])
parser.add_argument('--no-delete-old-files', help='do not delete files older than a day in the directory', dest="no_delete_old_files", action='store_true')
parser.add_argument('--result-count', help='Count of wallpapers to download', default=24,dest="result_count", type=int)
parser.add_argument('--page-count', help='Count of page results to download', default=2,dest="page_count", type=int)

args = parser.parse_args()

BASEURL = ""
cookies = dict()
topListRange = '1w'

BASEURL = 'https://wallhaven.cc/api/v1/search?apikey=' + api_key + '&topRange=' + topListRange + '&sorting=toplist&purity=100&ratios=' + str(args.force_aspect_ratio) + '&atleast=' + str(args.min_width) + 'x' + str(args.min_height) + '&page='

def downloadPage(pageId, totalImage):
    url = BASEURL + str(pageId)
    urlreq = requests.get(url, cookies=cookies)
    pagesImages = json.loads(urlreq.content);
    pageData = pagesImages["data"]

    for i in range(len(pageData)):
        currentImage = (((pageId - 1) * 24) + (i + 1))

        url = pageData[i]["path"]

        filename = os.path.basename(url)
        osPath = os.path.join(downloaded_dir, filename)
        if not os.path.exists(osPath):
            imgreq = requests.get(url, cookies=cookies)
            if imgreq.status_code == 200:
                if (args.verbose >= 1):
                    print("Downloading : %s - %s / %s" % (filename, currentImage , totalImage))
                with open(osPath, 'ab') as imageFile:
                    for chunk in imgreq.iter_content(1024):
                        imageFile.write(chunk)
            elif (imgreq.status_code != 403 and imgreq.status_code != 404):
                print("Unable to download %s - %s / %s" % (filename, currentImage , totalImage))
        else:
            if (args.verbose >= 1):
                print("%s already exist - %s / %s" % (filename, currentImage , totalImage))

def fix_path(dir):
    if not dir.endswith("/") and not dir.endswith("\\"):
        dir += "/"
    return dir

def delete_old_files(dir, keeptime):
    for f in os.listdir(dir):
        file = dir + f
        if os.stat(os.path.join(dir,f)).st_mtime < now - keeptime * 86400 and not search('^\..+?$', f):
            os.remove(file)

def main():
    dir = fix_path(args.directory)
    if not os.path.exists(dir):
        print(dir," is not a valid directory on the system")
        exit()
    else:
        if not args.no_delete_old_files:
            delete_old_files(args.directory, 1)

    pgid = args.page_count
    totalImageToDownload = str(args.result_count * pgid)
    for j in range(1, pgid + 1):
        downloadPage(j, totalImageToDownload)

if __name__ == "__main__":
    main()
