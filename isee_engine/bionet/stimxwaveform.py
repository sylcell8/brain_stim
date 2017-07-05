import numpy as np
import pandas as pd


class StimXWaveform(object):
    '''
    Extracellular Stimulating electrode
    '''

    def __init__(self, conf):
        waveform_config = self.get_waveform_config(conf)
        self.amp      = float(waveform_config["amp"]) # units? mA?
        self.delay    = float(waveform_config["del"]) # ms
        self.duration = float(waveform_config["dur"]) # ms

    def get_waveform_config(self, conf):
        return conf["extracellular_stimelectrode"]["waveform"] # to avoid having to change config location mult. places

    def is_active(self, simulation_time):
        stop_time = self.delay + self.duration
        return self.delay < simulation_time < stop_time

    def calculate(self, simulation_time):
        raise NotImplementedError("Implement specific waveform calculation")


class WaveformDC(StimXWaveform):

    def __init__(self, conf):
        StimXWaveform.__init__(self, conf)

    def calculate(self, t): # TODO better name
        if self.is_active(t):
            return self.amp
        else:
            return 0

class WaveformSin(StimXWaveform):

    def __init__(self, conf):
        StimXWaveform.__init__(self, conf)
        waveform_config = self.get_waveform_config(conf)
        self.freq         = float(waveform_config["freq"])   # Hz
        self.phase_offset = float(waveform_config["phase"])  # radians

    def calculate(self, t): # TODO better name

        if self.is_active(t):
            f = self.freq / 1000. # Hz to mHz
            a = self.amp
            return a * np.sin(2 * np.pi * f * t + self.phase_offset)
        else:
            return 0

## Factory ##

# mapping from 'shape' code to subclass, always lowercase
shape_classes = {
    'dc': WaveformDC,
    'sin': WaveformSin,
}

def waveform_factory(shape, conf):
    """
    :rtype: StimXWaveform
    """
    shape_key = shape.lower()

    if shape_key not in shape_classes:
        print "Warning: waveform shape not known" # throw error?

    Constructor = shape_classes[shape_key]

    return Constructor(conf)




