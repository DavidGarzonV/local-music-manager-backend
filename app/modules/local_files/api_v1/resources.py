import os
import eyed3
from flask import request, Blueprint
from app.common.utils import validateSongData

localfiles_v1_bp = Blueprint("localfiles_v1_bp", __name__)


def get_song_data(complete_path: str):
    try:
        song = eyed3.load(complete_path)

        if song and validateSongData(song):
            return song
    except Exception as e:
        print(e)

    return None


# Get the list of files in the directory
@localfiles_v1_bp.route("/", methods=["GET"])
def get_files():
    counter = 0

    args = request.args
    params = args.to_dict()

    music_directory = params.get("directory")

    # Validar si el directorio existe
    if music_directory is None:
        return {"Success": False, "Error": "The directory is required."}

    if not os.path.isdir(music_directory):
        return {"Success": False, "Error": "The directory does not exist."}

    filesList = []
    filesWithoutMetadata = []
    ENABLED_MUSIC_FORMATS = [
        "mp3",
        "m4a",
        "ogg",
        "wav",
        "wma",
    ]

    for root, directories, files in os.walk(music_directory):
        if root != music_directory:
            continue

        for file in sorted(files):
            file_extension = file.split(".")[-1].lower()

            if file_extension in ENABLED_MUSIC_FORMATS:
                complete_path = os.path.join(root, file)
                song = get_song_data(complete_path)

                if song is not None:
                    filesList.append(
                        {
                            "id": counter + 1,
                            "title": song.tag.title,
                            "artist": song.tag.artist,
                            "album": song.tag.album,
                            "file_name": file,
                            "complete_path": complete_path,
                            "complete_song_name": f"{song.tag.title} - {song.tag.artist}",
                        }
                    )
                else:
                    filesWithoutMetadata.append(
                        {
                            "id": counter + 1,
                            "file_name": file,
                            "complete_path": complete_path,
                        }
                    )

                counter += 1


    filesList.sort(key=lambda x: x["complete_song_name"])
    filesWithoutMetadata.sort(key=lambda x: x["file_name"])

    return {
        "Count": len(filesList),
        "Files": filesList,
        "FilesWithoutMetadata": filesWithoutMetadata,
    }
