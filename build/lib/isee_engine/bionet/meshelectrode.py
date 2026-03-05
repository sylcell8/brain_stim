import numpy as np
import math
import pandas as pd
import csv


class MeshXElectrode():

    def __init__(self, conf):

        self.conf = conf

        self.electrodes_mesh_file_dir = self.conf["extracellular_stimelectrode"]["electrodes_mesh_file_dir"]

        self.electrodes_mesh_file_name = self.conf["extracellular_stimelectrode"]["electrodes_mesh_file_name"]

        self.electrodes = self.conf["extracellular_stimelectrode"]["electrodes"]

        n_electrodes = len(self.electrodes)

        self.electrode_mesh = {}

        self.n_mesh = {}

    def make_mesh(self):

            for key in self.electrodes.keys():

                #Read electrode inputs
                electrode_x_length = self.electrodes[key]["x_length"]
                electrode_y_length = self.electrodes[key]["y_length"]
                mesh_nx = self.electrodes[key]["mesh_x"]
                mesh_ny = self.electrodes[key]["mesh_y"]
                nmesh = mesh_nx * mesh_ny
                self.n_mesh[key] = nmesh

                #compute mesh size
                dx = electrode_x_length / mesh_nx
                dy = electrode_y_length / mesh_ny

                grid_coor = np.zeros((3,nmesh))

                # for iy in range(mesh_ny):
                x = np.linspace(0, electrode_x_length, mesh_nx, endpoint= False) + dx / 2
                y = np.linspace(0, electrode_y_length, mesh_ny, endpoint= False) + dy / 2


                for ix in range(mesh_nx):
                    grid_coor[0, ix * mesh_ny: (ix + 1) * mesh_ny] = x[ix]
                    for iy in range(mesh_ny):
                        grid_coor[1, ix * mesh_ny + iy ] = y[iy]


                self.electrode_mesh[key] = grid_coor


    def write_mesh_to_separate_electrode_files(self):

        for key in self.electrodes.keys():

            file_name = self.electrodes_mesh_file_dir + "/" + self.electrodes_mesh_file_name + key + ".csv"

            with open(file_name, 'w') as f:
                writer = csv.writer(f, delimiter=' ')
                writer.writerow(["x_pos", "y_pos", "z_pos"])

                for imesh in range(self.n_mesh[key]):
                    writer.writerow([self.electrode_mesh[key][0][imesh],
                                     self.electrode_mesh[key][1][imesh], self.electrode_mesh[key][2][imesh]])
