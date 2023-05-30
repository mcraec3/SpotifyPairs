from spotify import Spotify
from pairings import pairs
import time

currtime = time.time()

sp = Spotify()

#While will become cron
#use get_current to check if playing currently first
while(time.time()-currtime < 60): 
    curr = sp.get_current()
    curr_id = curr['song_URL'].split("/")[-1]
    next = pairs.get(curr_id)

    if next is not None:
        line = ""
        with open("C:/Users/cmcra/www/lastcause.txt") as f:
            line = f.readline()
        if line.strip() != curr_id:
            with open("C:/Users/cmcra/www/lastcause.txt","w") as f:
                f.write(curr_id)            
            resp = sp.put_queue(push_uri="spotify:track:"+next)
    else:
        with open("C:/Users/cmcra/www/lastcause.txt","w") as f:
            f.write("")
#a.add_to_playlist()
#a.create_playlist(title="Test Playlist", desc="Ahoy")