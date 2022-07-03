from pytube import YouTube
from pytube import Playlist
from alive_progress import alive_bar
import validators
import moviepy.editor as mp
import os
import re
import sys

usage = """\
Usage: download_audio_yt.py [-h|c|u|l|p] "<music_path/url/urls.txt>" [OPTIONAL][-c|p] "<music_path>" [-c]
  -h/--help             - print this manual
  -u/--url              - download mp4 from playlist <url>
  -f/--file             - download mp4 from a list of playlists at <urls.txt>
  -p/--path             - specify custom download / music conversion location
  -c/--convert          - use at the end to convert downloaded mp4s to mp3s
     |--                 - use with -p to convert all mp4s in specified folder
     |--                 - use as only argument to convert all mp4s in /Music
  <url>                 - playlist url "https://www.youtube.com/playlist?list=xxx"
  <urls.txt>            - path to text file holding all urls of playlists to download
  <music_path>          - path to custom download folder\
"""


# DOWNLOAD PLAYLIST AND CONVERT TO AUDIO
def download_mp4_from_yt(playlist: Playlist, folder: str):
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
                # Download with oauth if content requires age verification
                bar.text = f'Download of {title} failed, re-trying with oauth...'
                YouTube(song_url, use_oauth=True, allow_oauth_cache=True).streams.filter(
                    file_extension='mp4').first().download(folder)
            bar()


def convert_mp4_to_mp3(folder: str):
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


def join_playlist_folder_to_path(playlist_url: str, folder: str):
    playlist = Playlist(playlist_url)
    return os.path.join(folder, playlist.title)


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
    folder = "Music"
    # Convert mp4s in Music/ dir to mp3s
    if sys.argv[1] in ["-c", "--convert"]:
        convert_mp4_to_mp3(folder)
        sys.exit(0)
    # Check if custom path set with convert flag
    if len(sys.argv) > 3:
        if sys.argv[1] in ["-p", "--path"] and sys.argv[3] in ["-c", "--convert"]:
            invalid_path_err(sys.argv[2])
            convert_mp4_to_mp3(sys.argv[2])
            sys.exit(0)
    # DOWNLOAD FROM URL
    if sys.argv[1] in ["-u", "--url"]:
        invalid_url_err(sys.argv[2])
        if sys.argv[3] in ["-p", "--path"]:
            invalid_path_err(sys.argv[4])
            folder = sys.argv[4]
        download_mp4_from_yt(
            Playlist(sys.argv[2]), join_playlist_folder_to_path(sys.argv[2], folder))
        if sys.argv[3] in ["-c", "--convert"] or sys.argv[5] in ["-c", "--convert"]:
            convert_mp4_to_mp3(
                join_playlist_folder_to_path(sys.argv[2]), folder)
        sys.exit(0)
    # DOWNLOAD FROM LIST OF URLS IN A TEXT FILE
    if sys.argv[1] in ["-f", "--file"]:
        inlavid_file_err(sys.argv[2])
        url_list = open(sys.argv[2]).readlines()
        # Check if path and list/url are set
        if sys.argv[3] in ["-p", "--path"]:
            invalid_path_err(sys.argv[4])
            folder = sys.argv[4]
        for playlist_url in url_list:
            invalid_url_err(playlist_url)
            download_mp4_from_yt(
                Playlist(playlist_url), join_playlist_folder_to_path(playlist_url, folder))
            if sys.argv[3] in ["-c", "--convert"] or sys.argv[5] in ["-c", "--convert"]:
                convert_mp4_to_mp3(
                    join_playlist_folder_to_path(playlist_url), folder)
        sys.exit(0)

# TODO
# redo CLI to:
# add -c at the end to convert, will only download by default [+]
# add -c to the path without -u/-l to only convert in specified path [+]
# add -c w/ other command to auto convert all files under Music dir [+]
# when downloading from a list of playlist, download and convert in parallel [-]


if __name__ == '__main__':
    cli()
