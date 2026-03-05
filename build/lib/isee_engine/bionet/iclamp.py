import numpy as np
import math
import pandas as pd
from neuron import h
import csv


class IClamp():

	def __init__(self, conf):

		self.conf = conf

		self.iclamp_amp = self.conf["iclamp"]["amp"]

		self.iclamp_del = self.conf["iclamp"]["del"]

		self.iclamp_dur = self.conf["iclamp"]["dur"]


	def attach_current(self, cell):

		self.cell = cell
		self.stim = h.IClamp(self.cell.hobj.soma[0](0.5))
		self.stim.delay = self.iclamp_del
		self.stim.dur = self.iclamp_dur
		self.stim.amp = self.iclamp_amp

		return self.stim




