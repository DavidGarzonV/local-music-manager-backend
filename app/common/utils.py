import datetime
import json
import os
import sys
import time
from difflib import SequenceMatcher


def if_song_has_title(song):
    if isinstance(song, str):
        return False

    if song.tag is None:
        return False

    if song.tag.title is None or len(song.tag.title) == 0 or song.tag.title == "":
        return False

    return True


def if_song_has_artist(song):
    if isinstance(song, str):
        return False

    if song.tag is None:
        return False

    if song.tag.artist is None or len(song.tag.artist) == 0 or song.tag.artist == "":
        return False

    return True


def validateSongData(song):
    return if_song_has_title(song) and if_song_has_artist(song)


def validateStringSimilarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def get_env_path():
    extDataDir = os.getcwd()
    if getattr(sys, "frozen", False):
        extDataDir = sys._MEIPASS

    return os.path.join(extDataDir, ".env")


def generate_expired_at(expires_in):
    now = datetime.datetime.now()
    expired_at = now + datetime.timedelta(seconds=expires_in)

    return time.mktime(expired_at.timetuple())


def create_folder_if_not_exists(folder):
    folder_path = os.path.join(os.path.dirname(__file__), "../" + folder)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def check_if_file_is_empty(file_path):
    try:
        f = open(file_path)
        data_json = json.load(f)
        return len(data_json) == 0
    except Exception:
        return True
