from difflib import SequenceMatcher
import os
import sys
import datetime
import time

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

