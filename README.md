# wallpapers.py

description: Download the top wallpapers for the day off of Reddit to a directory and delete files older than a day. 

prerequisites: have to create virtual environment if you're on one of the new Apple M1 MacBook Pros

running wallpapers.py:

```
mkdir ~venv/
python3 -m venv ~/venv
source ~/venv/bin/activate
python3 -m pip install PIL
python3 -m pip install requests
python3 -m pip install praw
python3 -m pip install imgurpython
./wallpapers.py
```
