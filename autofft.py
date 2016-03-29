"""Ideally this would show a FFT of the sound in real-time, but I haven't yet
figured out how to do that. So far it just records something and immediately
plots its FFT afterwards."""

from __future__ import division
import sys, os
import pyaudio, wave
import time
from show_transform import show_transform

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
DEFAULT_RECORD_SECONDS = 1
DEFAULT_COUNTDOWN_SECONDS = 0

p = pyaudio.PyAudio()

def listen(record_seconds, countdown_seconds, filename):
    recording = True
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    if countdown_seconds > 0:
        raw_input("Press Enter to start the countdown.")
        for i in xrange(countdown_seconds):
            print countdown_seconds - i,
            time.sleep(1)
    else:
        raw_input("Press Enter to start recording.")

    print "Recording...",

    frames = []
    for i in xrange(0, int(RATE/CHUNK * record_seconds)):
        data = stream.read(CHUNK)
        frames.append(data)

    print "Done. Processing data."

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return filename

def accept_time_input(ans, default=None):
    try:
        return int(ans)
    except ValueError:
        if default is not None and ans == "":
            return default
        else:
            print "Input not understood."
            sys.exit()

if __name__ == '__main__':
    ans = raw_input("Time to record? [%s s]: " % DEFAULT_RECORD_SECONDS)
    record_seconds = accept_time_input(ans, default=DEFAULT_RECORD_SECONDS)

    ans = raw_input("Countdown time? [%s s]: " % DEFAULT_COUNTDOWN_SECONDS)
    countdown_seconds = accept_time_input(ans,
        default=DEFAULT_COUNTDOWN_SECONDS)

    default_filename = "test.wav"
    filename = raw_input("A wav file will be created. Path to file? [%s]: "
        % default_filename)
    if filename == '': filename = default_filename

    if os.path.isfile(filename):
        ans = raw_input("File already exists. Overwrite? (y/[n]): ")
        if ans.lower() != "y":
            print "Quitting. Please try again."
            sys.exit()

    filename = listen(record_seconds, countdown_seconds, filename)
    show_transform(filename)