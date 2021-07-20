#!/usr/bin/python3
#
# https://github.com/Imgur/imgurpython
# https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html

import requests
import json
import praw
from re import search
import urllib.request
import os, sys, time
from time import time
from subprocess import call
from imgurpython import ImgurClient
from PIL import Image
from io import BytesIO
from warnings import simplefilter
import argparse
from fractions import Fraction
import mimetypes

now = time()
simplefilter('error', Image.DecompressionBombWarning)

home_dir = os.getenv('HOME') + "/"
cycle_dir = home_dir + "Pictures/Backgrounds/"
blacklist_dir = home_dir + "Pictures/Blacklisted Backgrounds/"
album_dir = home_dir + "Pictures/Album Backgrounds/"

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-v', '--verbose', action='count', help='increase the verbosity', default=0)
parser.add_argument('-a', '--album', nargs="*", help='download pictures using a imgur album id')
parser.add_argument('-d', '--directory', help='directory to save images to', default=cycle_dir)
parser.add_argument('-b', '--blacklisted', help='blacklist directory', default=blacklist_dir)
parser.add_argument('--min-width', help='min width of screen', default=1920, dest="min_width", type=int)
parser.add_argument('--min-height', help='min height of screen', default=1080, dest="min_height", type=int)
parser.add_argument('--max-height', help='max height of downloaded files', dest="max_height", default=10000, type=int)
parser.add_argument('--max-width', help='max width of downloaded files', dest="max_width", default=10000, type=int)
parser.add_argument('--force-aspect-ratio', help='only download files that match given aspect ratio', dest="force_aspect_ratio", choices=['25:16','3:2','5:4', '4:3', '16:10', '9:16', '16:9'])
parser.add_argument('--force-height', help='only download files that match given height', dest="force_height", type=int)
parser.add_argument('--force-width', help='only download files that match given width', dest="force_width", type=int)
parser.add_argument('-s','--subreddit', help='the subreddit to download pictures from', dest="subreddit", default="wallpapers+wallpaper+MinimalWallpaper")
parser.add_argument('--no-delete-old-files', help='do not delete files older than a day in the directory', dest="no_delete_old_files", action='store_true')
parser.add_argument('--search-term', nargs="*", help='search for a specific thing', dest="search_term")



args = parser.parse_args()

def main():
    args.directory = fix_path(args.directory)
    args.blacklisted = fix_path(args.blacklisted)

    directories = [args.directory,args.blacklisted]

    for dir in directories:
        dir = fix_path(dir)
        if not os.path.exists(dir):
            print(dir," is not a valid directory on the system")
            exit()

    if args.verbose >= 1 and args.force_aspect_ratio:
        print("Finding pictures with aspect ratio of", args.force_aspect_ratio)
    elif args.verbose >= 1 and not args.force_aspect_ratio and (not args.force_height or not args.force_width):
        print("Finding pictures with minimum resolution of", args.min_width, "x", args.min_height, "and maximum resolution of", args.max_width, "x",args.max_height)
    elif args.verbose >= 1 and not args.force_aspect_ratio and args.force_height or args.force_width:
        print("Finding pictures with exact resolution of", args.min_width, "x", args.min_height)

    if args.album:
        client_id= "6c478b24a403475"
        client_secret = "ebdf34952fad765ee2e0946de30933e4936c1f0d"
        client = ImgurClient(client_id, client_secret)
        for album in args.album:
            items = client.get_album_images(album)
            for picture in items:
                first_stage(picture.link)
    else:
        reddit = praw.Reddit(client_id='P31W4FjRB6gJ0Q', client_secret='mulKi79w35XYQPMngRoQKn_L_yk', user_agent='Wallpapers by /u/454Casull')
        subreddit = reddit.subreddit(args.subreddit)
        if args.search_term:
            for submission in subreddit.search(args.search_term):
                if not submission.over_18:
                    first_stage(submission.url)
        else:
            for submission in subreddit.top('day'):
                if not submission.over_18:
                    first_stage(submission.url)
        if not args.no_delete_old_files:
            delete_old_files(args.directory, 1)
            delete_old_files(args.blacklisted, 2)

def fix_path(dir):
    if not dir.endswith("/") and not dir.endswith("\\"):
        dir += "/"
    return dir

def get_filename(url):
    file = search('.+\/(.+)$', url)
    if file:
        return file.group(1)

def get_extension(file):
    ext = search('(\.....?)$', file)
    if ext is not None:
        return ext.group(1)

def get_image_size(url):
    file = get_filename(url)
    ext = get_extension(file)
    if ext is not None and file != "undefined.jpg" and is_url_image(url) is True:
        try:
            data = requests.get(url).content
            im = Image.open(BytesIO(data))
            width, height = im.size
        except Image.DecompressionBombWarning as e:
            width, height = -2, -2
        except Exception as e:
            width, height = -3, -3
    else:
        width, height = -1, -1
    return width, height

def is_url_image(url):
    mimetype,encoding = mimetypes.guess_type(url)
    return (mimetype and mimetype.startswith('image'))

def first_stage(url):
    name = get_filename(url)
    width, height = get_image_size(url)
    path = args.directory + name
    blacklist = args.blacklisted + name
    ratio = width / height

    second_stage(width, height, ratio, name, path, blacklist, url)

def second_stage(width, height, ratio, name, path, blacklist, url):
    ratio = str(Fraction(ratio).limit_denominator()).replace("/",":")

    fit_resolution_text = '[DOES FIT RESOLUTION] {0}\'s resolution is {1} x {2}'.format(name,width,height)
    not_fit_resolution_text = '[DOES NOT FIT RESOLUTION] {0}\'s resolution is {1} x {2}, needs to be between {3} x {4} and {5} x {6}'.format(name,width,height,args.min_width,args.min_height,args.max_width,args.max_height)
    fit_aspect_ratio_text = '[DOES FIT ASPECT RATIO] {0}\'s aspect ratio is {1}'.format(name,ratio)
    not_fit_aspect_ratio_text = '[DOES NOT FIT ASPECT RATIO] {0}\'s aspect ratio is {1}, needs to be {2}'.format(name,ratio,args.force_aspect_ratio)
    invalid_file_type_text = '[INVALID FILE TYPE] url: {0}'.format(url)
    bad_file_text = '[BAD FILE] url: {0}'.format(url)
    unknown_error_text = '[UNKNOWN ERROR] url: {0}, path {1}'.format(url,path)

    if not args.force_aspect_ratio and not args.force_width and not args.force_height:
        if args.max_width >= width >= args.min_width and args.max_height >= height >= args.min_height:
            third_stage(path,blacklist,name,url,width,height)
        else:
            if width == -1 and height == -1 and args.verbose > 1:
                print(invalid_file_type_text)
            elif width == -2 and height == -2 and args.verbose > 1:
                print(bad_file_text)
            elif width == -3 and height == -3 and args.verbose > 1:
                print(unknown_error_text)
            elif args.verbose > 1:
                print(not_fit_resolution_text)


    if args.force_aspect_ratio:
        if args.force_aspect_ratio == ratio:
            if args.verbose > 2:
                print(fit_aspect_ratio_text)
            third_stage(path,blacklist,name,url,width,height)
        else:
            if args.verbose > 1:
                print(not_fit_aspect_ratio_text)
                if args.verbose > 2:
                    print("\n")

    if args.force_width:
        if args.force_width == width:
            if args.verbose > 2:
                print(fit_resolution_text)
            third_stage(path,blacklist,name,url,width,height)
        else:
            if args.verbose >= 1:
                print(not_fit_resolution_text)
                if args.verbose > 2:
                    print("\n")

    if args.force_height:
        if args.force_height == height:
            if args.verbose > 2:
                print(fit_resolution_text)
            third_stage(path,blacklist,name,url,width,height)
        else:
            if args.verbose >= 1:
                print(not_fit_resolution_text)

def third_stage(path,blacklist,name,url,width,height):
    not_already_exists_text = '[DOES NOT EXIST] file path: {0}'.format(path)
    downloading_text = '[DOWNLOADING] url: {0}'.format(url)
    blacklisted_file_text = '[IN BLACKLIST] file: {0}'.format(name)
    not_blacklisted_file_text = '[NOT IN BLACKLIST] file: {0}'.format(name)
    already_exists_text = '[ALREADY EXISTS] file path: {0}'.format(path)

    if not os.path.exists(path):
        if args.verbose > 1:
            print(not_already_exists_text)
        if not os.path.exists(blacklist):
            if args.verbose > 2:
                print(not_blacklisted_file_text)
            if args.verbose > 0:
                print(downloading_text)
                if args.verbose > 2:
                    print("\n")
            download(path,url)
        elif args.verbose > 2:
            print(blacklisted_file_text)
    elif args.verbose > 1:
        print(already_exists_text)

def download(path,url):
    http_error_text = '[HTTP ERROR] file path: {0}'.format(url)
    try:
        urllib.request.urlretrieve(url, path)
    except urllib.error.HTTPError as e:
        if args.verbose > 0:
            print(http_error_text)

def check_aspect_ratio(ratio):
    ratio_nums = search('^(.*)\:+(.*)$', ratio)
    ratio_quotient = int(ratio_nums.group(1)) / int(ratio_nums.group(2))
    return(ratio_quotient)

def delete_old_files(dir, keeptime):
    for f in os.listdir(dir):
        file = dir + f
        if os.stat(os.path.join(dir,f)).st_mtime < now - keeptime * 86400 and not search('^\..+?$', f):
            os.remove(file)

def change_height():
    args.height = args.force_height
    args.min_height = args.force_height
    args.max_height = args.force_height

def change_width():
    args.width = args.force_width
    args.min_width = args.force_width
    args.max_width = args.force_width

if args.force_height:
    change_height()

if args.force_width:
    change_width()

if __name__ == "__main__":
    main()
