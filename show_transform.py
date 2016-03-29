import sys
import numpy as np
from scipy.signal import periodogram
from scipy.io import wavfile
import pyqtgraph as pg

def show_transform(filename):
    rate, data_stereo = wavfile.read(filename)
    x, y = periodogram(np.sum(data_stereo, axis=1), rate) # y is the PSD
    p = pg.plot(x, y)
    g = p.plotItem.graphicsItem()
    g.enableAutoRange(enable=False)
    p.plotItem.setLogMode(x=False, y=True)
    p.plotItem.setTitle("Power spectral density of <b>%s</b>" % filename)
    g.setMouseEnabled(y=False)

    # Set good-looking Y range (and workable X range)
    appx_noise_avg = np.log10(sum(y[len(y)//2:])/(len(y)/2))
    high = int(np.log10(max(y)))
    low = int(high - 1.11*(high - appx_noise_avg)) - 1
    p.setYRange(low, high)
    p.setYRange(low, high) # If I don't do it a second time, sometimes #1 fails
    p.setXRange(0, len(y)/2)

    # Pause to show graph
    raw_input("Press enter to quit")

if __name__ == "__main__":
    show_transform(sys.argv[1])