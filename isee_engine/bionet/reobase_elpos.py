import numpy as np
import math
import pandas as pd
import csv
import sys, os
from isee_engine.bionet import util
from scipy.spatial.distance import cdist

class MeshXElectrode():

    def __init__(self, conf):

        self.conf = conf

        # Reading the cell model_ids

        cells_file = self.conf["internal"]["cells"]

        self.cells_model_id = pd.read_csv(cells_file, sep = " ", header = "infer")["model_id"]

        # print self.cells_model_id

        # Reading the cell_model.csv file which contains the angle for aligning cells and name of morphology files

        bio_models_file = self.conf["internal"]["cell_models"]

        bio_models_df = pd.read_csv(bio_models_file, sep = " ", header = "infer")

        self.model_rotation = bio_models_df[bio_models_df["model_id"].isin(self.cells_model_id)]

        self.cells_info = self.model_rotation[["model_id", "rotation_angle_zaxis", "morphology"]]

        # print self.cells_info

        if (len(self.cells_model_id) != len(self.cells_info)):

            print len(self.cells_model_id), len(self.cells_info)
            print "ERROR: NOT ALL CELL MODELS FOUND IN cell_models.csv"
            print "EXITING EXCECUTION NOW"
            sys.exit()

        # Reading path to morphology files

        self.cell_morph_dir = self.conf["morphology"]["bio_morph_dir"]

        # Reading path to electrode files

        self.electrodes_mesh_file_dir = self.conf["extracellular_stimelectrode"]["electrodes_mesh_file_dir"]

        self.electrodes_mesh_file_name = self.conf["extracellular_stimelectrode"]["electrodes_mesh_file_name"]

        self.electrodes = self.conf["extracellular_stimelectrode"]["electrodes"]

        n_electrodes = len(self.electrodes)

        self.min_dist_from_cell = self.conf["extracellular_stimelectrode"]["min_dist_from_cell"]

        self.nonreobase_meshfile = self.conf["extracellular_stimelectrode"]["electrodes_mesh_file_name"]

        self.electrode_mesh = {}

        self.n_mesh = {}



    def read_swc_list(self):

        # Read swc files and find soma position
        self.swc_list = {}
        self.soma_pos = {}
        model_id = self.cells_info["model_id"]
        gid = 0

        for filename in self.cells_info["morphology"]:
            filepath = self.cell_morph_dir + "/" + filename
            self.swc_list[model_id[gid]] = pd.read_csv(filepath, header=2, sep = " ",
                                             names = ["id", "type", "x", "y", "z", "r", "pid"])
            self.soma_pos[model_id[gid]] = self.swc_list[model_id[gid]][self.swc_list[model_id[gid]]["type"] == 1][["x","y","z"]]
            self.swc_list[model_id[gid]] = self.swc_list[model_id[gid]][["x", "y", "z"]]

            if (self.soma_pos[model_id[gid]].empty):
                print "ERROR: CHECK THE NUMBER OF HEADER LINES FOR SWC OF THIS MODEL_ID:", model_id[gid]
                print "EXITING EXCECUTION NOW"
                sys.exit()

            gid += 1


    def align_cells_withyaxis(self):

        self.rotated_swc_list = {}

        # Rotate swc files for each model_id

        for model_id in self.swc_list:

            rotated_coor = np.zeros((len(self.swc_list[model_id]), 3)).T

            teta = self.cells_info[self.cells_info["model_id"] == model_id]["rotation_angle_zaxis"]

            RotZ = util.rotation_matrix([0,0,1], -teta)

            rotated_coor = np.dot(RotZ, self.swc_list[model_id][["x", "y", "z"]].T)

            self.rotated_swc_list[model_id] = pd.DataFrame(rotated_coor.T, columns=["x", "y", "z"])



    def make_spherical_mesh(self):

        N = 15; r = 1; rmin = 10; rmax = 100; rstep = 10

        grid_xyz = pd.DataFrame([])

        for r_prim in range(rmin, rmax, rstep):
            N_prim = N * (r_prim * r_prim) / (rmin * rmin)
            Ncount = 0
            a = (4 * np.pi * np.power(r, 2)) / N_prim
            d = np.sqrt(a)
            M_teta = np.round(np.pi / d)
            d_teta = (np.pi / M_teta)
            d_phi = a / d_teta
            for m in range(int(M_teta)):
                teta = np.pi * (m + 0.5) / M_teta
                M_phi = np.round(2 * np.pi * np.sin(teta) / d_phi)
                for n in range(int(M_phi)):
                    phi = (2 * np.pi * n) / M_phi
                    x = r_prim * np.sin(teta) * np.cos(phi)
                    y = r_prim * np.sin(teta) * np.sin(phi)
                    z = r_prim * np.cos(teta)
                    grid_xyz = grid_xyz.append(pd.DataFrame({"x" : x, "y" : y, "z" : z}, index=[0]), ignore_index=True)
                    Ncount += 1

        return grid_xyz




    def make_mesh_soma(self):

        grid = self.make_spherical_mesh()
        for model_id in self.soma_pos:
            file_name1 = self.electrodes_mesh_file_dir + "/" + str(model_id) + "original.csv"

        # First move the grid to around the soma for each model_id
        for model_id in self.soma_pos:
            file_name2 = self.electrodes_mesh_file_dir + "/" + str(model_id) + "stimXelectrodes.csv"
            soma_pos = pd.concat([self.soma_pos[model_id]] * len(grid), ignore_index=True)
            new_grid = grid + soma_pos

            with open(file_name1, 'w') as f1:
                new_grid.to_csv(f1, header=False, sep=' ', index=False)

            dist = cdist(new_grid, self.swc_list[model_id], metric='euclidean')
            min_dist = dist.min(axis=1)
            selected_elpoints = np.where(min_dist >= self.min_dist_from_cell)[0]
            selected_grid = [new_grid.iloc[i] for i in selected_elpoints]
            final_df = pd.DataFrame(selected_grid)
            with open(file_name2, 'w') as f2:
                final_df.to_csv(f2, header= False, sep = ' ', index=False)

            for el in range(len(final_df)):
                file_name3 = self.electrodes_mesh_file_dir + "/" + str(model_id) + "_" + str(el) + ".csv"
                with open(file_name3, 'w') as f3:
                    writer = csv.writer(f3, delimiter=' ')
                    writer.writerow(["ip", "electrode_mesh_file", "pos_x", "pos_y", "pos_z",
                                     "rotation_x", "rotation_y", "rotation_z", "waveform"])

                    writer.writerow(["0", self.nonreobase_meshfile, final_df.iloc[el][0],
                                     final_df.iloc[el][1],final_df.iloc[el][2], "0.", "0.", "0.", "waveform0.csv"])




