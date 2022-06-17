from pytube import YouTube
from pytube import Playlist
from alive_progress import alive_bar
import validators
import moviepy.editor as mp
import os
import re
import sys

usage = """\
Usage: download_audio_yt.py [-hul] "<url/textfile_with_urls>" [-p] "<download_path>"
  -h/--help             - <optional> print this manual
  -u/--url              - <required> download audio from <url>
  -l/--list             - <required> download audio list of playlists at <textfile_with_urls>
  <url>                 - <required> playlist url "https://www.youtube.com/playlist?list=xxx"
  <textfile_with_urls>  - <required> path to text file holding all urls of playlists to download
  -p/--path             - <optional> specify custom download location
  <download_path>       - <optional> path to custom download folder\
"""


# DOWNLOAD PLAYLIST AND CONVERT TO AUDIO
def download_from_yt(playlist: Playlist, folder: str):
    # DOWNLOAD ALL MP4S IN PLAYLIST
    print("Downloading %i items from playlist" % playlist.length)
    with alive_bar(playlist.length, dual_line=True) as bar:
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


def cli():
    # EXIT IF NONE OR TOO MANY ARGUMENTS
    if len(sys.argv) < 2 or len(sys.argv) > 5:
        print(usage)
        sys.exit(1)
    # PRINT HELP MENU
    if sys.argv[1] in ["-h", "--help"]:
        print(usage)
        sys.exit(0)
    # CHECK IF CUSTOM PATH SPECIFIED
    folder = "Music"
    if len(sys.argv) > 3:
        if sys.argv[3] in ["-p", "--path"]:
            if not os.path.exists(sys.argv[4]):
                print("Specified output folder %s does not exist..." %
                      sys.argv[4])
                sys.exit(1)
            folder = sys.argv[4]
    # DOWNLOAD FROM URL
    if sys.argv[1] in ["-u", "--url"]:
        if not validators.url(sys.argv[2]):
            print("URL %s not valid, quitting..." % sys.argv[2])
            sys.exit(1)
        playlist = Playlist(sys.argv[2])
        folder = os.path.join(folder, playlist.title)
        download_from_yt(playlist, folder)
        convert_to_mp3(folder)
    # DOWNLOAD FROM LIST OF URLS IN A TEXT FILE
    if sys.argv[1] in ["-l", "--list"]:
        if not os.path.isfile(sys.argv[2]):
            print("Playlist URL list %s does not exist..." %
                  sys.argv[2])
            sys.exit(1)
        url_list = open(sys.argv[2]).readlines()
        for playlist_url in url_list:
            if not validators.url(playlist_url):
                print("url %s not valid, quitting..." % sys.argv[2])
                sys.exit(1)
            playlist = Playlist(sys.argv[2])
            folder = os.path.join(folder, playlist.title)
            download_from_yt(playlist, folder)
            convert_to_mp3(folder)


# TODO
# redo CLI to:
# add -c at the end to convert, will only download by default
# add -c to the path without -u/-l to only convert in specified path
# add -c without any other command to automatically convert all files under current dir


if __name__ == '__main__':
    cli()
