import numpy as np
import math
import pandas as pd
import csv
import sys, os
from scipy.spatial.distance import cdist


class MeshXElectrode():

    def __init__(self, conf, rmin, rmax, rstep, Npoints, min_dist_tocell):

        self.conf = conf

        self.rmin = float(rmin)

        self.rmax = float(rmax)

        self.rstep = float(rstep)

        self.N_total = float(Npoints)

        self.min_dist_tocell = float(min_dist_tocell)

        cells_file = self.conf["internal"]["cells"]

        self.cells_model_id = pd.read_csv(cells_file, sep = " ", header = "infer")["model_id"]

        bio_models_file = self.conf["internal"]["cell_models"]

        bio_models_df = pd.read_csv(bio_models_file, sep = " ", header = "infer")

        self.model_info = bio_models_df[bio_models_df["model_id"].isin(self.cells_model_id)]

        self.cells_info = self.model_info[["model_id", "morphology"]]

        if (len(self.cells_model_id) != len(self.cells_info)):

            print len(self.cells_model_id), len(self.cells_info)
            print "ERROR: NOT ALL CELL MODELS FOUND IN cell_models.csv"
            print "EXITING EXCECUTION NOW"
            sys.exit()


        self.cell_morph_dir = self.conf["internal"]["bio_morph_dir"]

        self.electrodes_mesh_file_dir = self.conf["extracellular_stimelectrode"]["electrodes_mesh_file_dir"]

        self.nonreobase_meshfile = self.conf["extracellular_stimelectrode"]["electrodes_mesh_file_name"]

        self.electrode_mesh = {}

        self.n_mesh = {}



    def read_swc_list(self):

        # Read swc files and find soma position
        self.swc_list = {}
        self.soma_pos = {}
        self.soma_radius = {}
        model_id = self.cells_info["model_id"]
        gid = 0

        for filename in self.cells_info["morphology"]:
            filepath = self.cell_morph_dir + "/" + filename
            self.swc_list[model_id[gid]] = pd.read_csv(filepath, header=2, sep = " ",
                                             names = ["id", "type", "x", "y", "z", "r", "pid"])
            self.soma_pos[model_id[gid]] = self.swc_list[model_id[gid]][self.swc_list[model_id[gid]]["type"] == 1][["x","y","z"]]
            self.swc_list[model_id[gid]] = self.swc_list[model_id[gid]][["x", "y", "z", "r"]]

            if (self.soma_pos[model_id[gid]].empty):
                print "ERROR: CHECK THE NUMBER OF HEADER LINES FOR SWC OF THIS MODEL_ID:", model_id[gid]
                print "EXITING EXCECUTION NOW"
                sys.exit()

            gid += 1
            



    def move_swc_to_origin(self):

        swc_movedto_origin = {}

        for model_id in self.soma_pos:
            # soma_pos = pd.concat([self.soma_pos[model_id]] * len(self.swc_list[model_id]), ignore_index=True)
            x = self.swc_list[model_id]["x"] - float(self.soma_pos[model_id]["x"])
            y = self.swc_list[model_id]["y"] - float(self.soma_pos[model_id]["y"])
            z = self.swc_list[model_id]["z"] - float(self.soma_pos[model_id]["z"])
            swc_movedto_origin[model_id] = pd.DataFrame({"x" : x, "y" : y, "z" : z})
            file_name = self.electrodes_mesh_file_dir + "/" + str(model_id) + "swc_movedto_origin.csv"
            with open(file_name, 'w') as f:
                swc_movedto_origin[model_id].to_csv(f, header=False, sep=' ', index=False)

        return swc_movedto_origin




    def make_spherical_mesh(self):

        """
        make a spherical mesh around 0,0,0
        For this it requires the total number of mesh points, rmin, rmax and rstep
        """

        #Check rmin and rmax and see how many spheres we have
        print "check that: rmin < rmax)"
        print "check that: (rmax - rmin) > rstep"

        if (self.rmin == self.rmax):
            r = self.rmin
            self.rstep = 1
            n_sphere = 1
        else:
            n_sphere = int((self.rmax-self.rmin) / self.rstep)

        sphere_r = {}
        for sphere in range(n_sphere):
            sphere_r[sphere] = self.rmin + sphere * self.rstep


        sphere_npoint = int(self.N_total / n_sphere)

        grid_xyz = pd.DataFrame([])
        sphere_count = 0

        for r in sphere_r.values():
            Ncount = 0
            a = (4 * np.pi) / sphere_npoint
            d = np.sqrt(a)
            M_teta = np.round(np.pi / d)
            d_teta = (np.pi / M_teta)
            d_phi = a / d_teta
            for m in range(int(M_teta)):
                teta = np.pi * (m + 0.5) / M_teta
                M_phi = np.round(2 * np.pi * np.sin(teta) / d_phi)

                for n in range(int(M_phi)):
                    phi = (2 * np.pi * n) / M_phi
                    x = r * np.sin(teta) * np.cos(phi)
                    y = r * np.sin(teta) * np.sin(phi)
                    z = r * np.cos(teta)
                    grid_xyz = grid_xyz.append(pd.DataFrame({"x" : x, "y" : y, "z" : z}, index=[0]), ignore_index=True)
                    Ncount += 1

            sphere_count += 1

        file_name = self.electrodes_mesh_file_dir + "/" + "original_mesh.csv"
        with open(file_name, 'w') as f:
            grid_xyz.to_csv(f, header=False, sep=' ', index=False)

        return grid_xyz




    def make_mesh_soma(self):

        grid = self.make_spherical_mesh()
        swc_movedto_origin = self.move_swc_to_origin()
        print swc_movedto_origin

        for model_id in self.soma_pos:
            file_name = self.electrodes_mesh_file_dir + "/" + str(model_id) + "stimXelectrodes.csv"

            dist = cdist(grid, swc_movedto_origin[model_id], metric='euclidean')
            min_dist = dist.min(axis=1)


            selected_elpoints = np.where(min_dist >= self.min_dist_tocell)[0]
            selected_grid = [grid.iloc[i] for i in selected_elpoints]
            if (selected_elpoints.size == 0):
                print "All the points are closer than ", self.min_dist_tocell , "to some cell's part"
                print "Choose a smaller rmin"

            final_df = pd.DataFrame(selected_grid)
            with open(file_name, 'w') as f:
                final_df.to_csv(f, header= False, sep = ' ', index=False)

            for el in range(len(final_df)):
                file_name3 = self.electrodes_mesh_file_dir + "/" + str(model_id) + "_" + str(el) + ".csv"
                with open(file_name3, 'w') as f3:
                    writer = csv.writer(f3, delimiter=' ')
                    writer.writerow(["ip", "electrode_mesh_file", "pos_x", "pos_y", "pos_z",
                                     "rotation_x", "rotation_y", "rotation_z", "waveform"])

                    writer.writerow(["0", self.nonreobase_meshfile, final_df.iloc[el][0],
                                     final_df.iloc[el][1],final_df.iloc[el][2], "0.", "0.", "0.", "waveform0.csv"])

