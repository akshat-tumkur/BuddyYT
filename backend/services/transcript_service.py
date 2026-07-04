from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled
import re

def get_transcript(url):
    video_id = re.search(r"v=([a-zA-Z0-9_-]+)", url).group(1)

    try:
        fetched_transcript = YouTubeTranscriptApi().fetch(video_id, languages=['en'])
        transcript_list = fetched_transcript.to_raw_data()
        transcript = " ".join(chunk["text"] for chunk in transcript_list)
        
        
    except TranscriptsDisabled:
        print("No captions available for this video.")
    except Exception as e:
        print(f"An error occurred: {e}")
        exit()

    return transcript