import numpy as np
import pandas as pd


class StimXWaveform(object):
    """
    Waveform of extracellular stimulating electrode
    """

    def __init__(self, waveform_config):
        self.amp      = float(waveform_config["amp"]) # units? mA?
        self.delay    = float(waveform_config["del"]) # ms
        self.duration = float(waveform_config["dur"]) # ms

    def is_active(self, simulation_time):
        stop_time = self.delay + self.duration
        return self.delay < simulation_time < stop_time

    def calculate(self, simulation_time):
        raise NotImplementedError("Implement specific waveform calculation")


class WaveformDC(StimXWaveform):
    """
    DC (step) waveform
    """

    def __init__(self, waveform_config):
        StimXWaveform.__init__(self, waveform_config)

    def calculate(self, t): # TODO better name
        if self.is_active(t):
            return self.amp
        else:
            return 0

class WaveformSin(StimXWaveform):
    """
    Sinusoidal waveform
    """

    def __init__(self, waveform_config):
        StimXWaveform.__init__(self, waveform_config)
        self.freq         = float(waveform_config["freq"])   # Hz
        self.phase_offset = float(waveform_config["phase"])  # radians

    def calculate(self, t): # TODO better name

        if self.is_active(t):
            f = self.freq / 1000. # Hz to mHz
            a = self.amp
            return a * np.sin(2 * np.pi * f * t + self.phase_offset)
        else:
            return 0

class WaveformCustom:
    """
    Custom waveform defined by csv file
    """

    def __init__(self, waveform_file, wf_dir):
        self.definition = pd.read_csv(wf_dir + waveform_file, sep='\t')

    def calculate(self, t):
        return np.interp(t, self.definition["time"], self.definition["amplitude"])


## Factory ##

# mapping from 'shape' code to subclass, always lowercase
shape_classes = {
    'dc': WaveformDC,
    'sin': WaveformSin,
}

def waveform_factory(conf):
    """
    :rtype: StimXWaveform
    """
    waveform_conf = conf["extracellular_stimelectrode"]["waveform"]

    if type(waveform_conf) in (str,unicode): # if waveform_conf is str or unicode assume to be name of file in stim_dir
        wf_dir = conf["manifest"]["$STIM_DIR"] + "/"
        return WaveformCustom(waveform_conf,wf_dir)

    shape = waveform_conf["shape"]
    shape_key = shape.lower()

    if shape_key not in shape_classes:
        print "Warning: waveform shape not known" # throw error?

    Constructor = shape_classes[shape_key]

    return Constructor(waveform_conf)




