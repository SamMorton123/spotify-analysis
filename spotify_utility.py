import datetime
import pandas as pd
import spotipy
import spotipy.util as util

FILE = 'history.xlsx'
username = 'Sam Morton'
client_id ='b850ae9d84a5417baf2b6632cdb21fe4'
client_secret = '602a9396ebab48208fc3ded8bfa5d8d5'
redirect_uri = 'http://localhost:9000'
scope = 'user-read-recently-played'
TOKEN = util.prompt_for_user_token(username=username, 
                                   scope=scope, 
                                   client_id=client_id,   
                                   client_secret=client_secret,     
                                   redirect_uri=redirect_uri)
COLLECTED_LOC = 6
ARTIST = 1
ALBUM = 2
SONG = 3

def get_timestamp():
    today = datetime.datetime.today()

    dt_obj = datetime.datetime.strptime('{}.{}.{} {}:{}:{}'.format(today.day, today.month, today.year, today.hour, today.minute, today.second), 
        '%d.%m.%Y %H:%M:%S')
    ts = dt_obj.timestamp() * 1000

    return ts

# very inefficient sorting of the dict
def sort_by_plays(plays):
    new = {}
    keys = list(plays.keys())
    while len(keys) > 0:
        mkey = None
        mval = -1
        for key in keys:
            if plays[key] > mval:
                mkey = key
                mval = plays[key]
        new[mkey] = mval
        keys.remove(mkey)
    return new

def write_history():
    collection_date = get_timestamp()

    sp = spotipy.Spotify(auth=TOKEN)
    df = pd.read_excel(FILE, header=0)

    # get most recent collected timestamp
    last = df.iloc[0, 5]

    recents = sp.current_user_recently_played(after=last)

    ids = []
    for track in recents['items']:
        ids.append(track['track']['id'])

    i = len(ids) - 1
    while i > -1:
        res = sp.track(ids[i])
        row = pd.DataFrame({'Artist': res['artists'][0]['name'], 'Album': res['album']['name'], 'Song': res['name'], 'Timestamp': recents['items'][i]['played_at'], 'Time Collected': collection_date}, index=[0])
        df = pd.concat([row, df]).reset_index(drop=True)
        i -= 1
    
    df = df[['Artist', 'Album', 'Song', 'Timestamp', 'Time Collected']]
    df.to_excel(FILE)

def top(select = ARTIST):

    df = pd.read_excel(FILE, header=0)

    counts = {}
    for i in range(len(df.index)):
        sel = df.iloc[i, select]
        if sel not in counts: counts[sel] = 1
        else: counts[sel] += 1
    
    counts = sort_by_plays(counts)

    i = 1
    for s in counts:
        print('{}. {} - {} ({}%)'.format(i, s, counts[s], round((counts[s] / len(df.index)) * 100, 2)))
        i += 1
        

write_history()
top(select=ARTIST)
