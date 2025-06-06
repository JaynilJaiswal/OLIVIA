from youtube_dl import YoutubeDL
import ytm

api = ytm.YouTubeMusic()


def getMusicDetails(search_text):

    if search_text =="":
        return [0,0,0,0]

    songs = api.search_songs(search_text)
    id = [k['id'] for k in songs['items']]
    song_name = [k['name'] for k in songs['items']]
    explicit = [k['explicit'] for k in songs['items']]
    url = [k['thumbnail']['url'] for k in songs['items']]

    if (id[0] == None):
        return [0,0,0,0]

    return [id,song_name,explicit,url]

def getMusicFile_key(youtube_id,name):
    print(name)
    filename = str(name)+".m4a"
    audio_downloader = YoutubeDL({'format': 'bestaudio/best', 'outtmpl': filename})
    audio_downloader.extract_info("https://www.youtube.com/watch?v="+str(youtube_id))
    return "Streaming "+ name+" now!"


