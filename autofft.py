"""Ideally this would show a FFT of the sound in real-time, but I haven't yet
figured out how to do that. So far it just records something and immediately
plots its FFT afterwards."""

from __future__ import division
import sys, os
import pyaudio, wave
import numpy as np
import time
from PyQt4 import QtCore as core, QtGui as gui
from show_transform import setup_plot, show_transform, show_transform_file, pg

CHUNK = 4096
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
DEFAULT_RECORD_SECONDS = 1
DEFAULT_COUNTDOWN_SECONDS = 0

p = pyaudio.PyAudio()

def listen_file(record_seconds, countdown_seconds, filename):
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

class Listener(core.QObject):
    new_chunk = core.pyqtSignal(bytearray)

    def __init__(self):
        super(Listener, self).__init__()

        self.stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        self.thread = core.QThread()
        self.thread.setObjectName("listener thread")

        print "creating singleShot"
        core.QTimer.singleShot(0, self.thread.start)

        self.moveToThread(self.thread)
        self.thread.started.connect(self.run)

    def run(self):
        self.cont = True

        while self.cont:
            self.new_chunk.emit(bytearray(self.stream.read(CHUNK)))
            #time.sleep(1)

        self.stream.close()

    def stop(self):
        # Call this from a different thread
        self.cont = False

def run_realtime():
    if FORMAT != pyaudio.paInt16:
        raise Exception("This version hacked together; need FORMAT=paInt16")

    app = gui.QApplication([])

    def name_main_thread():
        core.QThread.currentThread().setObjectName("main")
    core.QTimer.singleShot(0, name_main_thread)

    plot, curve = setup_plot()
    def plot_here(bytearray_stereo):
        chunk_arr = np.frombuffer(bytearray_stereo, dtype=np.int16)
        chunk_arr = chunk_arr.reshape((len(chunk_arr)/2, 2))
        show_transform(RATE, chunk_arr, plot=plot, curve=curve)

    listener = Listener()
    listener.new_chunk.connect(plot_here)

    app.exec_()

def run_record():
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

    filename = listen_file(record_seconds, countdown_seconds, filename)
    show_transform_file(filename)

if __name__ == '__main__':
    ans = raw_input("Enter A for real-time, B for record: ")
    if ans.lower() == "a":
        run_realtime()
    elif ans.lower() == "b":
        run_record()
    else:
        print "Input not understood. Quitting. Please try again."
        sys.exit()