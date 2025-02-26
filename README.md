# Wallpaper Downloaders

## Mac M1 Virtual Environment Setup

Create Virtual Environment

```
mkdir ~venv/
python3 -m venv ~/venv
```

## Wallhaven.cc Wallpaper Downloader

Download the top wallpapers for the week off of Wallhaven.cc to a directory and delete files older than a day.

**Usage**

```shell
./wallhaven-wallpapers.py
```

**Arguments**

| Variable | Description       | Choices | `[Default]`     |
| -------- | ----------------- | :------: | --------------- |
| `-v --verbose` | increase the verbosity |  | `0` |
| `-d --directory` | directory to save images to |  | `~/Pictures/Backgrounds/Downloaded Backgrounds/` |
| `--min-width` | min width of image |  | `1920` |
| `--min-height` | min height of image |  | `1080` |
| `--force-aspect-ratio` | only download files that match the given aspect ratio | `'25:16','3:2','5:4', '4:3', '16:10', '9:16', '16:9'` | `10000` |
| `--no-delete-old-files` | do not delete files older than a day in the directory | | N/A |
| `--result-count` | Count of wallpapers to download | | `24` |
| `--page-count` | Count of page results to download | | `2` |
| `--deletion-time` | time in seconds that files will be deleted after | | `604800` |
| `-p --purge` | purge files in folder before downloading new images | | `false` |

## Reddit Wallpaper Downloader

Download the top wallpapers for the day off of Reddit to a directory and delete files older than a day.

**Prerequisites**

```shell
python3 -m pip install Pillow requests praw imgurpython
```

**Usage**

```shell
./reddit-wallpapers.py
```

**Arguments**

| Variable | Description       | Choices | `[Default]`     |
| -------- | ----------------- | :------: | --------------- |
| `-v --verbose` | increase the verbosity |  | `0` |
| `-a --album` | download pictures using a imgur album id |  | N/A |
| `-d --directory` | directory to save images to |  | `~/Pictures/Backgrounds/Downloaded Backgrounds/` |
| `-b --blacklisted` | blacklist directory for images that shouldn't be downloaded again |  | `~/Pictures/Backgrounds/Blacklisted Backgrounds/` |
| `--min-width` | min width of image |  | `1920` |
| `--min-height` | min height of image |  | `1080` |
| `--max-height` | max height of image |  | `10000` |
| `--max-width` | max width of image |  | `10000` |
| `--force-aspect-ratio` | only download files that match the given aspect ratio | `'25:16','3:2','5:4', '4:3', '16:10', '9:16', '16:9'` | `10000` |
| `--force-height` | only download files that match given height | | N/A |
| `--force-width` | only download files that match given width | | N/A |
| `-s --subreddit` | the subreddit to download pictures from | | `wallpapers+wallpaper+MinimalWallpaper` |
| `--no-delete-old-files` | do not delete files older than a day in the directory | | N/A |
| `--search-term` | search wallpapers for a specific term | | N/A |
| `--deletion-time` | time in seconds that files will be deleted after | | `86400` |
