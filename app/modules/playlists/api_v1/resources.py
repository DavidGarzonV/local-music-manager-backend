from flask import request, Blueprint
from app.common.yt_music import create_playlist, get_playlist_tracks, get_youtube_music_playlists

playlists_v1_bp = Blueprint("playlists_v1_bp", __name__)


@playlists_v1_bp.route("/", methods=["GET"])
def get_playlists():
    playlists = get_youtube_music_playlists()
    if len(playlists) == 0:
        return {
            "Success": False,
            "Error": "No playlists were found in the YouTube Music account",
        }

    playlists = [
        p for p in playlists if p["playlistId"] != "LM" and p["playlistId"] != "SE"
    ]

    playlists = [
        {
            "title": p["title"],
            "playlistId": p["playlistId"],
            "thumbnails": p["thumbnails"],
        }
        for p in playlists
    ]

    return {
        "Success": True,
        "Playlists": playlists,
    }


@playlists_v1_bp.route("/", methods=["POST"])
def create_playlist_method():
    data = request.get_json()
    name = data.get("name")

    if name is None or len(name) == 0 or name == "":
        return {
            "Success": False,
            "Error": "The name of the playlist is required",
        }

    description = data.get("description", "")
    privacyStatus = data.get("privacyStatus", "PRIVATE")

    playlist_id = create_playlist(name, description, privacyStatus)

    return {
        "Success": True,
        "PlaylistId": playlist_id,
    }


@playlists_v1_bp.route("/<string:id>", methods=["GET"])
def get_playlist(id):
    tracks = get_playlist_tracks(id)

    return {
        "Success": True,
        "Tracks": tracks,
    }