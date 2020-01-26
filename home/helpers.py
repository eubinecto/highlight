#for extracting a video ID from youtube url
import re
#for getting the transcript of a video
from youtube_transcript_api import YouTubeTranscriptApi

# extracting a video ID from url
def extract_vid_id(url):
    result = re.findall(pattern='.+?v=(.+)$',
                        string=url)
    return result[0]
#A url to be inserted into the YT player code.
#A url to be inserted into the YT player code.
def generateYTURL(vid_id, start_sec):
    return "https://www.youtube.com/embed/" + vid_id + "?start=" + str(start_sec) + "&cc_load_policy=1"

def generate_player(vid_id, start_sec):
    url = generateYTURL(vid_id=vid_id,
                        start_sec=start_sec)
    return """
           <iframe
           class='embed-responsive-item'
           src='{}'
           gesture='media'
           allow='encrypted-media'
           allowfullscreen>
           </iframe>
           """.format(url)


def get_tracks(vid_id):
    tracks = []
    raw = YouTubeTranscriptApi.get_transcript(vid_id, languages=['en'])
    for track_dict in raw:
        tracks.append(track_dict['text'].strip())
    return tracks


def highlight_tracks_whole(tracks_whole,
                           summary):
    highlights = []
    for item in summary:
        highlights.append(item[0])

    for highlight in highlights:
        tracks_whole = tracks_whole.replace(highlight,"<mark><strong>{}</strong></mark>".format(highlight))


    return tracks_whole

#for generating vectors.


