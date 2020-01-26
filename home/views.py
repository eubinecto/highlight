from django.shortcuts import render
from .forms import VideoURLForm

from .helpers import extract_vid_id, generate_player, get_tracks, highlight_tracks_whole

#for doing the summary work
from .summary import pre_process, get_embeddings, make_clusters, generate_summary

import numpy as np
import json

# Create your views here.
def get_url(request):

    if request.method == 'POST':
        form = VideoURLForm(request.POST)

        if form.is_valid():
            url = form.cleaned_data['url']
            # now... what do I do with this?

            #get the video id
            vid_id = extract_vid_id(url=url)
            player = generate_player(vid_id=vid_id,
                                     start_sec=0)
            #get the tracks.
            tracks = get_tracks(vid_id=vid_id)
            #just do this
            tracks_whole = " ".join(tracks)


            #pre-process the tracks
            processed = pre_process(tracks=tracks,
                                    max_length=100,
                                    stride=4)
            num_pp_sentences = len(processed)
            n_clusters = int(num_pp_sentences * 0.10)

            #generate embeddings
            try:
                #load it, and parse it back to numpy array
                vectors = np.asarray(json.loads(request.session[vid_id]))
            except KeyError:
                #clear the session
                request.session.clear()
                #get the vector, then store it in session
                vectors = get_embeddings(processed=processed)
                request.session[vid_id] = json.dumps(vectors.tolist())

            #now generate clusters
            clusters = make_clusters(processed=processed,
                                     vectors=vectors,
                                     n_clusters=n_clusters)

            #and generate the summary
            summary = generate_summary(clusters=clusters,
                                       processed=processed,
                                       tracks=tracks)

            highlighted = highlight_tracks_whole(tracks_whole=tracks_whole,
                                                 summary=summary)

            context_dict = {'summary':summary,
                           'vid_id': vid_id,
                           'player': player,
                           'highlighted': highlighted}

            return render(request, './home/result.html', context_dict)

    else:
        #just create an empty form
        form = VideoURLForm()


    return render(request, './home/search.html', {'form': form})

