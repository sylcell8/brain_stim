from isee_engine.bionet import util
from isee_engine.bionet import bionet_io
from isee_engine.bionet.stimxwaveform import stimx_waveform_factory
import numpy as np
import math
import pandas as pd
from neuron import h
import sys, os


class StimXElectrode():
    '''
    Extracellular Stimulating electrode
    '''

    def __init__(self, conf): # TODO doesn't need to know about entire conf file
        '''
        Create an array
        '''
        self.stim_dir = conf["manifest"]["$STIM_DIR"] + "/"

        #Reading electrode position
        stimelectrode_position_file = conf["extracellular_stimelectrode"]["position"]
        stimelectrode_position_df = pd.read_csv(stimelectrode_position_file, sep=' ')

        self.elmesh_file = stimelectrode_position_df['electrode_mesh_file']
        self.elpos = stimelectrode_position_df.as_matrix(columns=['pos_x', 'pos_y', 'pos_z']).T
        self.elrot = stimelectrode_position_df.as_matrix(columns=['rotation_x', 'rotation_y', 'rotation_z'])
        self.elnsites = self.elpos.shape[1] #Number of electrodes in electrode file
        self.waveform = stimx_waveform_factory(conf)

        self.trans_X = {}  # mapping segment coordinates
        self.waveform_amplitude = []
        self.el_mesh = {}
        self.el_mesh_size = []

        self.read_electrode_mesh()
        self.rotate_the_electrodes()
        self.place_the_electrodes()


    def read_electrode_mesh(self):

        el_counter = 0
        for file in self.elmesh_file:
            mesh = pd.read_csv(self.stim_dir + file, sep=" ")
            mesh_size = mesh.shape[0]
            self.el_mesh_size.append(mesh_size)

            self.el_mesh[el_counter] = np.zeros((3, mesh_size))
            self.el_mesh[el_counter][0] = mesh['x_pos']
            self.el_mesh[el_counter][1] = mesh['y_pos']
            self.el_mesh[el_counter][2] = mesh['z_pos']
            el_counter += 1


    def place_the_electrodes(self):

        transfer_vector = np.zeros((self.elnsites,3))

        for el in range(self.elnsites):

            mesh_mean = np.mean(self.el_mesh[el], axis= 1 )
            transfer_vector[el] = self.elpos[:, el] - mesh_mean[:]

        for el in range(self.elnsites):
            new_mesh = self.el_mesh[el].T + transfer_vector[el]
            self.el_mesh[el] = new_mesh.T



    def rotate_the_electrodes(self):

        for el in range(self.elnsites):

            phi_x = self.elrot[el][0]
            phi_y = self.elrot[el][1]
            phi_z = self.elrot[el][2]

            RotX = util.rotation_matrix([1,0,0], phi_x)
            RotY = util.rotation_matrix([0,1,0], phi_y)
            RotZ = util.rotation_matrix([0,0,1], phi_z)
            RotXY = RotX.dot(RotY)
            RotXYZ = RotXY.dot(RotZ)

            new_mesh = np.dot(RotXYZ, self.el_mesh[el])
            self.el_mesh[el] = new_mesh



    def set_transfer_resistance(self, gid, seg_coords):

        rho = 300.0 # ohm cm
        r05 = seg_coords['p05']
        nseg = r05.shape[1]
        cell_map = np.zeros((self.elnsites, nseg))
        for el in xrange(self.elnsites):

            mesh_size = self.el_mesh_size[el]

            for k in range(mesh_size):

                rel = np.expand_dims(self.el_mesh[el][:,k], axis=1)
                rel_05 = rel - r05
                r2 = np.einsum('ij,ij->j', rel_05, rel_05)
                r = np.sqrt(r2)
                if (all(i >= 10 for i in r) == False):
                    bionet_io.print2log0('ERROR:External electrode is too close')
                    sys.exit()
                cell_map[el, :] += 1. / r

        cell_map *= (rho / (4 * math.pi)) * 0.01
        self.trans_X[gid] = cell_map

 
    def calculate_waveforms(self, tstep):
        simulation_time = h.dt * tstep
        # copies waveform elnsites times (homogeneous)
        self.waveform_amplitude = np.zeros(self.elnsites) + self.waveform.calculate(simulation_time)



    def get_vext(self, gid):

          waveform_per_mesh = np.divide(self.waveform_amplitude, self.el_mesh_size)
          v_extracellular = np.dot(waveform_per_mesh, self.trans_X[gid]) * 1E6
          vext_vec = h.Vector(v_extracellular)

          return vext_vec




          # print (v_extracellular ==0 )
          # v_extracellular = 0
          # for el in range(self.elnsites):
          #     waveform_per_mesh = self.interpolated_waveform_amplitude[el][self.tstep -1] /  self.el_mesh_size[el]
          #     v_extracellular +=  waveform_per_mesh * self.trans_X[gid] * 1E6
          # v_extracellular_flat = v_extracellular.flatten()
          # vext_vec = h.Vector(v_extracellular_flat)

          # for i in range(int(vext_vec.size())):
          #     if (vext_vec.x[i] != 0.):
          #         print vext_vec.x[i]



#     def get_vext(self, cell):
#         self.cell = cell
#         trans_X = self.trans_X[self.cell.gid]
#         i_ext_step = len(self.waveform_amplitude)
#         self.vext[self.cell.gid] = np.zeros((i_ext_step, self.nseg))
#         for i in range(i_ext_step):
#             i_ext = self.waveform_amplitude[i]
#             self.vext[self.cell.gid][i,:] = trans_X * i_ext * 1E6
#         return self.vext
#
#
# #Here we play vext on ref_e_extracellular at t_vec
#     def set_stimulation(self,cell):
#         self.cell = cell
#         t_vec = h.Vector(self.waveform_time)
#         self.t_vec = t_vec
#         seg_counter=0
#         for sec in cell.hobj.all:
#             for seg in sec:
#                     v_ext_seg = self.vext[self.cell.gid][:, seg_counter]
#                     v_ext_segVec = h.Vector(v_ext_seg)
#                     self.vext_list.append(v_ext_segVec)
#                     v_ext_segVec.play(seg._ref_e_extracellular, self.t_vec, 1)
#                     seg_counter+=1



   # def interpolate_waveform(self, nsteps):
   #
   #      self.nstep = nsteps
   #
   #      self.interpolated_waveform_amplitude = np.zeros((self.elnsites, self.nstep + 1))
   #      interpolated_waveform_time = np.zeros(self.nstep + 1)
   #
   #      for i in range(self.nstep + 1):
   #          interpolated_waveform_time[i] = i * h.dt
   #
   #      for el in range(self.elnsites):
   #          self.interpolated_waveform_amplitude[el] = \
   #              np.interp(interpolated_waveform_time, self.waveform_time, self.all_waveform_amplitude.values[:,el])
   #
   #
   #
   #
   #  def get_vext(self, tstep, gid):
   #
   #        self.tstep = tstep
   #
   #        waveform_per_mesh = np.divide(self.interpolated_waveform_amplitude[:,self.tstep -1], self.el_mesh_size)
   #
   #        v_extracellular = np.dot(waveform_per_mesh, self.trans_X[gid]) * 1E6
   #
   #        vext_vec = h.Vector(v_extracellular)
   #
   #        return vext_vec
   #

