from isee_engine.bionet import util,bionet_io
import isee_engine.bionet.biophysical as bio
import isee_engine.bionet.morphology as mor

import neuron
from neuron import h
import os, sys
import neuron.gui
import numpy as np
import pandas as pd
import csv
import math
import json


class CellPDB():
    def __init__(self, conf, out_path):

        self.bionet_dir = os.path.dirname(__file__)

        h.load_file(self.bionet_dir + '/biophysical.hoc')

        h.load_file(self.bionet_dir + '/import3d.hoc')

        self.outpath = str(out_path)

        self.conf = conf

        cells_file = self.conf["internal"]["cells"]

        cells_model_id = pd.read_csv(cells_file, sep=" ", header="infer")["model_id"]

        cell_locs = pd.read_csv(cells_file, sep=" ", header="infer", )[["x_soma", "y_soma", "z_soma"]]

        bio_models_file = self.conf["internal"]["cell_models"]

        bio_models_df = pd.read_csv(bio_models_file, sep=" ", header="infer")

        self.model_info = bio_models_df[bio_models_df["model_id"].isin(cells_model_id)]  # data frame of cell_models.csv

        # self.cells_info = self.model_info[["model_id", "morphology"]]

        if (len(cells_model_id) != len(self.model_info)):
            print len(cells_model_id), len(self.model_info)
            print "ERROR: NOT ALL CELL MODELS FOUND IN cell_models.csv"
            print "EXITING EXCECUTION NOW"
            sys.exit()

        self.cell_morph_dir = self.conf["internal"]["bio_morph_dir"]

        index = 0

        for row in self.model_info.itertuples():

            model_id = row.model_id
            morphology_file = row.morphology
            model_type = row.fixaxon
            self.morph_path = str(self.cell_morph_dir) + "/" + str(morphology_file)
            hobj = h.Biophysical()
            bio.set_morphology(hobj, self.morph_path)

            morphology = mor.Morphology(hobj)
            soma_pos = morphology.get_soma_pos()
            soma_loc = cell_locs.iloc[index]
            index += 1
            translate_vector = soma_pos - soma_loc

            output_name = "swc" + "_" + str(model_id) + ".pdb"
            output = self.outpath + "/" + output_name
            with open(output, 'w') as f:
                for sec in hobj.allsec():
                    section_name = sec.name().split(".")[1][:4]
                    if section_name == 'axon':
                        n = int(h.n3d())
                        for i in range(n):
                            f.write('%s %6s %s %11.3f%8.3f%8.3f %s %s\n' % ("ATOM", index,
                                                                            " S   PRO A   1",
                                                                            h.x3d(i) - translate_vector[0],
                                                                            h.y3d(i) - translate_vector[1],
                                                                            h.z3d(i) - translate_vector[2],
                                                                            " 1.00",
                                                                            " 1.00"))
                    else:
                        n = int(h.n3d())
                        for i in range(n):
                            f.write('%s %6s %s %11.3f%8.3f%8.3f %s %s\n' % ("ATOM", index,
                                                                           " C   PRO A   1",
                                                                           h.x3d(i) - translate_vector[0],
                                                                           h.y3d(i) - translate_vector[1],
                                                                           h.z3d(i) - translate_vector[2],
                                                                           " 1.00",
                                                                           " 1.00"))


        index = 0

        for row in self.model_info.itertuples():

            model_id = row.model_id
            morphology_file = row.morphology
            model_type = row.fixaxon
            self.morph_path = str(self.cell_morph_dir) + "/" + str(morphology_file)
            hobj = h.Biophysical()
            bio.set_morphology(hobj, self.morph_path)

            if model_type == 'perisomatic':
                bio.fix_axon_perisomatic(hobj)

            if model_type == 'all_active':
                bio.fix_axon_all_active(hobj)

            morphology = mor.Morphology(hobj)
            soma_pos = morphology.get_soma_pos()
            soma_loc = cell_locs.iloc[index]
            index += 1
            translate_vector = soma_pos - soma_loc

            output_name = str(model_type) + "_" + str(model_id) + ".pdb"
            output = self.outpath + "/" + output_name
            with open(output, 'w') as f:
                for sec in hobj.allsec():
                    section_name = sec.name().split(".")[1][:4]
                    if section_name == 'axon':
                        n = int(h.n3d())
                        for i in range(n):
                            f.write('%s %6s %s %11.3f%8.3f%8.3f %s %s\n' % ("ATOM", index,
                                                                            " S   PRO A   1",
                                                                            h.x3d(i) - translate_vector[0],
                                                                            h.y3d(i) - translate_vector[1],
                                                                            h.z3d(i) - translate_vector[2],
                                                                            " 1.00",
                                                                            " 1.00"))
                    else:
                        n = int(h.n3d())
                        for i in range(n):
                            f.write('%s %6s %s %11.3f%8.3f%8.3f %s %s\n' % ("ATOM", index,
                                                                           " C   PRO A   1",
                                                                           h.x3d(i) - translate_vector[0],
                                                                           h.y3d(i) - translate_vector[1],
                                                                           h.z3d(i) - translate_vector[2],
                                                                           " 1.00",
                                                                           " 1.00"))

