import numpy as np
import math
import pandas as pd
import csv
import sys
from scipy import signal

class Reobase_waveform():

    def __init__(self, conf):

        self.conf = conf
      
        waveform_shape = self.conf["reobase_waveform"]["shape"]

        self.number_of_grid = self.conf["reobase_waveform"]["number_of_grid"]

        self.stim_dur = self.conf["reobase_waveform"]["stimulation_duration"]

        self.delay_between_electrodes = self.conf["reobase_waveform"]["delay_between_electrodes"]

        self.total_stim_dur = (self.stim_dur + self.delay_between_electrodes) * self.number_of_grid

        self.simulation_dt = self.conf["reobase_waveform"]["simulation_dt"]

        self.stimulation_dir = self.conf["extracellular_stimelectrode"]["electrodes_mesh_file_dir"]


        if waveform_shape == "pulse":

            self.pulse_waveform(self.conf)

        elif waveform_shape == "sinusoid":

            self.sinusoid_waveform()


    def pulse_waveform(self,conf):

        pulse_prop = self.conf["reobase_waveform"]["pulse"]
        delay_between_electrodes = self.conf["reobase_waveform"]["delay_between_electrodes"]
        init_pulse_amplitude = pulse_prop["amp"]
        increment_amplitude = pulse_prop["inc_amp"]
        pulse_delay = pulse_prop["del"]
        pulse_duration = pulse_prop["dur"]
        number_of_pulses = self.stim_dur / (pulse_duration + pulse_delay)

        it_dic = {}
        time = 0
        init_amp = 0.
        inc = 1
        it_dic["time"] = []
        it_dic["amp"] = []
        it_dic["time"].append(time)
        it_dic["amp"].append(init_amp)
        it_dic["amp"].append(init_amp)

        # Writing the time
        for npulse in np.arange(number_of_pulses + 1):
            time = time + pulse_delay
            for m in range(2):
                it_dic["time"].append(time)
                it_dic["amp"].append(init_amp + inc * increment_amplitude)
            time = time + pulse_duration
            for m in range(2):
                it_dic["time"].append(time)
                it_dic["amp"].append(init_amp)
            inc += 1


        it_dic["amp"] = it_dic["amp"][:-1]
        it_df =  pd.DataFrame(it_dic)
        it_df = it_df[it_df["time"] <= self.stim_dur]


        for ngrid in range(self.number_of_grid):
            output_waveform_dir = self.stimulation_dir + "/waveform" + str(ngrid) + ".csv"
            time = pd.DataFrame(it_df["time"] * 1000 + (self.delay_between_electrodes + self.stim_dur) * 1000 * ngrid)
            amp = pd.DataFrame(-1 * it_df["amp"])
            final_df = time.join(amp)
            colnames = ["time", "amplitude"]
            final_df.columns = colnames
            final_df.to_csv(output_waveform_dir, sep='\t', index=False)



    def sinusoid_waveform(self):
        pass
