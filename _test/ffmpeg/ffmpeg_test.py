import ffmpeg
import json
from pathlib import Path
import pprint # Used for pretty-printing the output

file_path = "/Users/douglasgarrett/Documents/pictures/2025_pictures/2025-08_FL_visitors/2025-08_FL_visitors_videos/PXL_20250805_234716743.mp4"

try:
    # Use ffmpeg.probe to get all available metadata
    metadata = ffmpeg.probe(file_path, loglevel='quiet')

    # Print the full metadata dictionary
    # pprint.pprint(metadata)

    # save to a json file
    script_path = Path(__file__).resolve()
    with open(script_path.parent / "ffmpeg_metadata.json", "w") as json_file:
        json.dump(metadata, json_file, indent=4) # indent for pretty-printing

    # print(metadata['format'])  # General format information

    # Access specific, low-level stream information
    # video_stream = next(s for s in metadata['streams'] if s['codec_type'] == 'video')
    # print("\nVideo Stream Details:")
    # print(f"Codec: {video_stream.get('codec_name')}")
    # print(f"Resolution: {video_stream.get('width')}x{video_stream.get('height')}")
    # print(f"FPS: {video_stream.get('avg_frame_rate')}")

    # audio_stream = next(s for s in metadata['streams'] if s['codec_type'] == 'audio')
    # print("\nAudio Stream Details:")
    # print(f"Codec: {audio_stream.get('codec_name')}")
    # print(f"Sample Rate: {audio_stream.get('sample_rate')}")

except ffmpeg.Error as e:
    print(f"An error occurred: {e.stderr.decode()}")

