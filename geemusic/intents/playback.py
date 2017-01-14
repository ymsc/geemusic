from flask_ask import statement, audio
from os import environ
from geemusic import ask, queue, app
from geemusic.utils.music import GMusicWrapper

##
# Callbacks
#
@ask.on_playback_stopped()
def stopped(offset):
    queue.paused_offset = offset
    app.logger.debug("Stopped at %s" % offset)

@ask.on_playback_started()
def started(offset):
    app.logger.debug("Started at %s" % offset)

@ask.on_playback_nearly_finished()
def nearly_finished():
    next_id = queue.up_next()

    if next_id != None:
        api = GMusicWrapper.generate_api()
        stream_url = api.get_stream_url(next_id)

        return audio().enqueue(stream_url)

@ask.on_playback_finished()
def nearly_finished():
    next_id = queue.next()

##
# Intents
#
@ask.intent('AMAZON.StartOverIntent')
def resume():
    next_id = queue.current()

    if next_id == None:
        return audio("There are no songs on the queue")
    else:
        api = GMusicWrapper.generate_api()
        stream_url = api.get_stream_url(next_id)

        return audio().enqueue(stream_url)

@ask.intent('AMAZON.ResumeIntent')
def resume():
    return audio('Resuming').resume()

@ask.intent('AMAZON.PauseIntent')
def pause():
    return audio('Pausing').stop()

@ask.intent('AMAZON.StopIntent')
def stop():
    queue.reset()
    return audio('Stopping').stop()

@ask.intent('AMAZON.NextIntent')
def next_song():
    next_id = queue.next()

    if next_id == None:
        return audio("There are no more songs on the queue")
    else:
        api = GMusicWrapper.generate_api()
        stream_url = api.get_stream_url(next_id)

        return audio().play(stream_url)

@ask.intent('AMAZON.PreviousIntent')
def prev_song():
    prev_id = queue.prev()

    if prev_id == None:
        return audio("You can't go back any farther in the queue")
    else:
        api = GMusicWrapper.generate_api()
        stream_url = api.get_stream_url(prev_id)

        return audio().play(stream_url)

@ask.intent("AMAZON.ShuffleOnIntent")
def shuffle_on():
    if len(queue.song_ids) == 0:
        return statement("There are no songs to shuffle.")
    api = GMusicWrapper.generate_api()

    # Start streaming the first track in the new shuffled list
    first_song_id = queue.shuffle_mode(True)
    stream_url = api.get_stream_url(first_song_id)

    return audio().enqueue(stream_url)

@ask.intent("AMAZON.ShuffleOffIntent")
def shuffle_off():
    if len(queue.song_ids) == 0:
        return statement("There are no songs to unshuffle.")
    api = GMusicWrapper.generate_api()

    # Start streaming the first track in the new shuffled list
    first_song_id = queue.shuffle_mode(False)
    stream_url = api.get_stream_url(first_song_id)

    return audio().enqueue(stream_url)


@ask.intent('GeeMusicCurrentlyPlayingIntent')
def currently_playing():
    if queue.map_user_uploaded_songs.isAlive() is True:
        return statement("Please wait for your tracks to finish indexing")

    track = queue.current_track()

    if track is None:
        return audio("Nothing is playing right now")

    return audio("The current track is %s by %s" % (track['title'], track['artist']))

@ask.intent("GeeMusicThumbsUpIntent")
def thumbs_up():
    if len(queue.song_ids) == 0:
        return statement("Please play a song to vote")

    if queue.map_user_uploaded_songs.isAlive() is True:
        return statement("Please wait for your tracks to finish indexing")
    api = GMusicWrapper.generate_api()
    api.rate_song(queue.current_track(), '5')
    # api.rate_song('5')

    return statement("Upvoted")


@ask.intent("GeeMusicThumbsDownIntent")
def thumbs_down():
    if len(queue.song_ids) == 0:
        return statement("Please play a song to vote")

    if queue.map_user_uploaded_songs.isAlive() is True:
        return statement("Please wait for your tracks to finish indexing")
    api = GMusicWrapper.generate_api()
    api.rate_song(queue.current_track(), '1')

    return statement("Downvoted")
