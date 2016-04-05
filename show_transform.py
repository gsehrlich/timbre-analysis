import sys
import numpy as np
from scipy.signal import periodogram
from scipy.io import wavfile
import pyqtgraph as pg

def setup_plot():
    p = pg.plot()
    curve = p.plotItem.plot()

    g = p.plotItem.graphicsItem()
    g.enableAutoRange(enable=False)
    p.plotItem.setLogMode(x=False, y=True)
    p.plotItem.setTitle("Power spectral density")
    g.setMouseEnabled(y=False)

    return p, curve

def show_transform(rate, data_stereo, plot=None, curve=None):
    x, y = periodogram(np.sum(data_stereo, axis=1), rate) # y is the PSD
    if plot is None: plot = pg.plot(x[y != 0], y[y != 0])
    else: curve.setData(x[y != 0], y[y != 0])

    """
    # Set good-looking Y range
    appx_noise_avg = np.log10(sum(y[len(y)//2:])/(len(y)/2))
    high = int(np.log10(max(y)))
    low = int(high - 1.11*(high - appx_noise_avg)) - 1
    plot.setYRange(low, high)
    plot.setYRange(low, high) # If I don't do it a second time, sometimes #1 fails
    """

def show_transform_file(filename):
    rate, data_stereo = wavfile.read(filename)
    p, curve = setup_plot()
    show_transform(rate, data_stereo, curve)
    p.plotItem.setTitle("Power spectral density of <b>%s</b>" % filename)

    # Pause to show graph
    raw_input("Press enter to quit")

if __name__ == "__main__":
    show_transform_file(sys.argv[1])