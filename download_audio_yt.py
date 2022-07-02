from pytube import YouTube
from pytube import Playlist
from alive_progress import alive_bar
import validators
import moviepy.editor as mp
import os
import re
import sys

usage = """\
Usage: download_audio_yt.py [-h|u|l|c|p] "<url/textfile_with_urls/music_path>" [-c|p] "<music_path>" [-c]
  -h/--help             - <optional> print this manual
  -u/--url              - <required> download audio from playlist <url>
  -l/--list             - <required> download audio from a list of playlists at <textfile_with_urls>
  -p/--path             - <optional> specify custom download location
  -c                    - <optional> use to convert downloaded mp4s to mp3s
  <url>                 - <required> playlist url "https://www.youtube.com/playlist?list=xxx"
  <textfile_with_urls>  - <required> path to text file holding all urls of playlists to download
  <music_path>          - <optional> path to custom download folder\
"""


# DOWNLOAD PLAYLIST AND CONVERT TO AUDIO
def download_from_yt(playlist: Playlist, folder: str):
    # DOWNLOAD ALL MP4S IN PLAYLIST
    print("Downloading %i items from playlist" % len(playlist))
    with alive_bar(len(playlist), dual_line=True) as bar:
        for song_url in playlist:
            title = YouTube(song_url).title
            # YouTube(song_url).streams.filter(only_audio=True).first().download(folder)
            bar.text = f'-> Downloading {title}, please wait...'
            try:
                YouTube(song_url).streams.filter(
                    file_extension='mp4').first().download(folder)
            except KeyError:
                bar.text = f'Download of {title} failed, re-trying with oauth...'
                YouTube(song_url, use_oauth=True, allow_oauth_cache=True).streams.filter(
                    file_extension='mp4').first().download(folder)
            bar()


def convert_to_mp3(folder: str):
    # LOOP THROUGH LIST DOWNLOADED FILES AND CONVERT TO MP3
    for file in os.listdir(folder):
        if re.search('mp4', file):
            # print("Converting %s" % os.path.basename(file))
            mp4_path = os.path.join(folder, file)
            mp3_path = os.path.join(folder, os.path.splitext(file)[0] + '.mp3')
            new_file = mp.AudioFileClip(mp4_path)
            new_file.write_audiofile(mp3_path)
            new_file.close()
            os.remove(mp4_path)


def setargs_download(playlist_url: str, folder: str, convert: bool):
    playlist = Playlist(playlist_url)
    folder = os.path.join(folder, playlist.title)
    download_from_yt(playlist, folder)
    if convert:
        convert_to_mp3(folder)


def invalid_url_err(playlist_url: str):
    if not validators.url(playlist_url):
        print("URL %s not valid, quitting..." % playlist_url)
        sys.exit(1)


def inlavid_file_err(file: str):
    if not os.path.isfile(file):
        print("Playlist URL list %s does not exist..." %
              file)
        sys.exit(1)


def invalid_path_err(file: str):
    if not os.path.exists(file):
        print("Specified output folder %s does not exist..." %
              file)
        sys.exit(1)


def cli():
    # EXIT IF NONE OR TOO MANY ARGUMENTS
    if len(sys.argv) < 2 or len(sys.argv) > 6:
        print(usage)
        sys.exit(1)
    # PRINT HELP MENU
    if sys.argv[1] in ["-h", "--help"]:
        print(usage)
        sys.exit(0)
    convert = False
    folder = "Music"
    # Convert mp4s in current dir to mp3s
    if sys.argv[1] in ["-c", "--convert"]:
        convert_to_mp3(folder)
        sys.exit(0)
    # Check if custom path set with convert flag
    if len(sys.argv) > 3:
        if sys.argv[1] in ["-p", "--path"] and sys.argv[3] in ["-c", "--convert"]:
            invalid_path_err(sys.argv[2])
            convert_to_mp3(sys.argv[2])
            sys.exit(0)
        # Check if path and list/url are set
        if sys.argv[3] in ["-p", "--path"]:
            invalid_path_err(sys.argv[4])
            folder = sys.argv[4]
        if sys.argv[3] in ["-c", "--convert"] or sys.argv[5] in ["-c", "--convert"]:
            convert = True
    # DOWNLOAD FROM URL
    if sys.argv[1] in ["-u", "--url"]:
        invalid_url_err(sys.argv[2])
        setargs_download(sys.argv[2], folder, convert)
        sys.exit(0)
    # DOWNLOAD FROM LIST OF URLS IN A TEXT FILE
    if sys.argv[1] in ["-l", "--list"]:
        inlavid_file_err(sys.argv[2])
        url_list = open(sys.argv[2]).readlines()
        for playlist_url in url_list:
            invalid_url_err(playlist_url)
            setargs_download(playlist_url, folder, convert)
        sys.exit(0)

# TODO
# redo CLI to:
# add -c at the end to convert, will only download by default [+]
# add -c to the path without -u/-l to only convert in specified path [+]
# add -c without any other command to automatically convert all files under current dir [+]
# when downloading from a list of playlist, download and convert in parallel [-]


if __name__ == '__main__':
    cli()
