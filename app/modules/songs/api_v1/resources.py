from flask import request, Blueprint
from app.common.code_logger import APP_LOGGER
from app.common.yt_music import (
    search_on_youtube_music,
    add_items_to_playlist,
    get_song,
)
from concurrent.futures import ThreadPoolExecutor

songs_v1_bp = Blueprint("songs_v1_bp", __name__)


@songs_v1_bp.route("/search-songs", methods=["POST"])
def search_songs():
    data = request.get_json()
    songs = data.get("songs")

    executor = ThreadPoolExecutor()
    songTasks = []

    for song in songs:
        identifier = song.get("identifier")
        title = song.get("title")

        if title is None or len(title) == 0 or title == "":
            continue

        artist = song.get("artist")
        if artist is None or len(artist) == 0 or artist == "":
            continue

        original_name = song.get("originalName")
        complete_path = song.get("completePath")

        song_to_search = {
            "identifier": identifier,
            "title": title,
            "artist": artist,
            "original_name": original_name,
            "complete_path": complete_path,
        }

        f = executor.submit(search_on_youtube_music, song_to_search)
        songTasks.append(f)

    songsResults = []
    for task in songTasks:
        searchResults = task.result()

        if "Title" in searchResults:
            songsResults.append(
                {
                    "SongIdentifier": searchResults.get("SongIdentifier"),
                    "SongTitle": searchResults.get("Title"),
                    "SongArtist": searchResults.get("Artist"),
                    "SongOriginalName": searchResults.get("OriginalName"),
                    "SongCompletePath": searchResults.get("CompletePath"),
                    "SearchResults": {
                        "BestMatch": searchResults.get("BestMatch"),
                        "AdditionalResults": searchResults.get("AdditionalResults"),
                    },
                }
            )

    return {"Success": True, "Songs": songsResults}, 200


@songs_v1_bp.route("/save-songs", methods=["POST"])
def save_songs():
    data = request.get_json()
    songs = data.get("songs")
    if songs is None or len(songs) == 0:
        return {"Success": False, "Error": "No songs were provided."}, 400

    playlist_id = data.get("playlist_id")
    if playlist_id is None or len(playlist_id) == 0 or playlist_id == "":
        return {"Success": False, "Error": "Playlist ID is required."}, 400

    try:
        if len(songs) > 0:
            result = add_items_to_playlist(playlist_id, songs)

            if result.get("Success") is False:
                return result, 500

            return result, 200

        return {
            "Success": True,
            "AddedVideosIds": [],
            "NotAddedVideos": [],
        }, 200
    except Exception as e:
        APP_LOGGER.error("Error saving songs")
        APP_LOGGER.error(e)

    return {"Success": False, "AddedVideos": 0, "AlreadyInPlaylist": 0}, 500


@songs_v1_bp.route("/<string:video_id>", methods=["GET"])
def get_video_id(video_id):
    if video_id is None or len(video_id) == 0 or video_id == "":
        return {"Success": False, "Error": "Video ID is required."}, 400

    try:
        song = get_song(video_id)
        return {"Success": True, "Song": song["videoDetails"]}, 200
    except Exception as e:
        APP_LOGGER.error("Error getting song")
        APP_LOGGER.error(e)

    return {"Success": False, "Song": None}, 500
