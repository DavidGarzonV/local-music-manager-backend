from ytmusicapi import YTMusic
from app.common.code_logger import APP_LOGGER
from app.common.error_handling import UnauthorizedException
from app.common.utils import validateStringSimilarity
from app.config import (
    OAUTH_FILE,
)
from app.modules.auth.api_v1.utils import refresh_token_from_session

similarity_ratio = 0.6

def catch_ytmusic_exceptions(exception):
    APP_LOGGER.error("Error YTMusic: ")
    error_reason = exception.args[0]

    if "HTTP 401" in error_reason:
        APP_LOGGER.error("HTTP 401: Unauthorized.")
        raise UnauthorizedException()


def create_youtube_music_session():
    try:
        ytmusic = YTMusic(OAUTH_FILE)
        return ytmusic
    except Exception as e:
        APP_LOGGER.error("Error creating YTMusic instance: ")
        catch_ytmusic_exceptions(e)


def check_connection(secondAttempt=False):
    try:
        ytmusic = create_youtube_music_session()
        ytmusic.get_library_playlists(limit=1)

        return True
    except Exception:
        # Attempt to refresh token
        response = refresh_token_from_session()
        if response is not False:
            if not secondAttempt:
                return check_connection(True)

        return False


def get_youtube_music_playlists():
    ytmusic = create_youtube_music_session()
    try:
        playlists = ytmusic.get_library_playlists(limit=None)
        return playlists
    except Exception as e:
        APP_LOGGER.error("Error getting playlists: ")
        catch_ytmusic_exceptions(e)

        return []


def get_formatted_result(result, best_match=None, is_video=False):
    album = ""
    if "album" in result and result["album"] is not None:
        album = result["album"]["name"]

    # search for artist in original song
    if len(result["artists"]) == 0:
        base_song = get_song(result["videoId"])["videoDetails"]
        result["artists"] = [
            {
                "name": base_song["author"],
                "id": base_song["channelId"],
            }
        ]

    return {
        "resultType": result["resultType"],
        "videoId": result["videoId"],
        "title": result["title"],
        "artists": result["artists"],
        "album": album,
        "thumbnails": result["thumbnails"],
        "duration": result["duration"],
        "isBestMatch": not is_video
        and (
            (best_match is not None and result["videoId"] == best_match["videoId"])
            or best_match is None
        ),
    }


def clean_search_results(results):
    results = results[:5]

    results_with_video_id = [
        x for x in results if "videoId" in x and x["videoId"] is not None
    ]

    # clear video id duplicates
    seen = set()
    results_with_video_id = [
        x
        for x in results_with_video_id
        if x["videoId"] not in seen and not seen.add(x["videoId"])
    ]

    results_with_video_id = sorted(
        results_with_video_id, key=lambda x: x["resultType"] == "song", reverse=True
    )

    return results_with_video_id


def search_best_match(original_title, original_artist, song_results, is_video=False):
    best_match = None
    item_ratio = []

    if len(song_results) == 0:
        return {
            "BestMatch": None,
            "AdditionalResults": [],
        }

    for item in song_results:
        artists = item.get("artists", [])
        artist = ""

        if len(artists) > 0:
            artist = artists[0].get("name")

        similarity_title = validateStringSimilarity(original_title, item.get("title"))
        similarity_artist = validateStringSimilarity(original_artist, artist)
        total_similarity = similarity_title + similarity_artist

        if similarity_artist == 0:
            total_similarity = total_similarity - 0.5

        item_ratio.append(
            {
                "match": item,
                "similarity_title": similarity_title,
                "similarity_artist": similarity_artist,
                "total_similarity": total_similarity,
            }
        )

    # sort by similarity
    item_ratio = sorted(
        item_ratio,
        key=lambda x: x["total_similarity"],
        reverse=True,
    )

    best_match = item_ratio[0]["match"]

    # from item_ratio get only match
    item_results = [x["match"] for x in item_ratio]

    # Remove best match from list
    item_results = [x for x in item_results if x["videoId"] != best_match["videoId"]]

    # add to the beginning of the list
    item_results.insert(0, best_match)

    # limit results
    if is_video:
        item_results = item_results[:2]
    else:
        item_results = item_results[:5]

    for i in range(len(item_results)):
        item_results[i] = get_formatted_result(item_results[i], best_match, is_video)

    return {
        "BestMatch": get_formatted_result(best_match),
        "AdditionalResults": item_results,
    }


def search_on_youtube_music(song_to_search):
    identifier = song_to_search.get("identifier")
    title = song_to_search.get("title")
    artist_to_find = song_to_search.get("artist")
    original_name = song_to_search.get("original_name")
    complete_path = song_to_search.get("complete_path")

    ytmusic = create_youtube_music_session()
    artist = artist_to_find.strip()

    try:
        search_song_results = ytmusic.search(
            query=f"{title} {artist}",
            filter="songs",
            scope=None,
            limit=20,
            ignore_spelling=False,
        )
        search_song_results = clean_search_results(search_song_results)
        song_result = search_best_match(title, artist, search_song_results)
        song_best_match = song_result.get("BestMatch")
        song_additional_results = song_result.get("AdditionalResults")

        return {
            "SongIdentifier": identifier,
            "Title": title,
            "Artist": artist,
            "OriginalName": original_name,
            "CompletePath": complete_path,
            "BestMatch": song_best_match,
            "AdditionalResults": song_additional_results,
        }
    except Exception as e:
        APP_LOGGER.error("Error searching on YouTube Music: ")
        catch_ytmusic_exceptions(e)
        return {
            "SongIdentifier": identifier,
            "Title": title,
            "Artist": artist,
            "OriginalName": original_name,
            "CompletePath": complete_path,
            "BestMatch": None,
            "AdditionalResults": [],
        }


def add_items_to_playlist(playlist_id, video_ids):
    ytmusic = create_youtube_music_session()

    set_videos = set(video_ids)
    no_duplicates = list(set_videos)

    result = ytmusic.add_playlist_items(
        playlistId=playlist_id, videoIds=no_duplicates, duplicates=True
    )

    if result.get("status") == "STATUS_FAILED":
        return {"Success": False}
    else:
        playlist_edit_results = result.get("playlistEditResults")
        playlist_edit_results = [x["videoId"] for x in playlist_edit_results]

        songs_not_added = [x for x in no_duplicates if x not in playlist_edit_results]

        return {
            "Success": True,
            "AddedVideosIds": playlist_edit_results,
            "NotAddedVideos": songs_not_added,
        }


def get_playlist_tracks(playlist_id):
    ytmusic = create_youtube_music_session()
    try:
        playlist = ytmusic.get_playlist(playlist_id, None)
        tracks = playlist.get("tracks", [])
        tracks = [x["videoId"] for x in tracks]

        return tracks
    except Exception as e:
        APP_LOGGER.error("Error getting playlist tracks: ")
        catch_ytmusic_exceptions(e)
        return []


def get_song(video_id):
    ytmusic = create_youtube_music_session()
    try:
        return ytmusic.get_song(video_id)
    except Exception as e:
        APP_LOGGER.error("Error getting song: ")
        catch_ytmusic_exceptions(e)
        return None


def create_playlist(title, description, privacy_status="PRIVATE"):
    ytmusic = create_youtube_music_session()
    try:
        playlist_id = ytmusic.create_playlist(title, description, privacy_status)
        return playlist_id
    except Exception as e:
        APP_LOGGER.error("Error creating playlist: ")
        catch_ytmusic_exceptions(e)
        return False
