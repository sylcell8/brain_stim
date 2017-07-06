import os
from neuron import h
import numpy as np
import csv
from isee_engine.bionet import util,bionet_io
from isee_engine.bionet.electrode import Electrode
from isee_engine.bionet.stimxelectrode import StimXElectrode
from isee_engine.bionet.iclamp import IClamp
from time import time

pc = h.ParallelContext()    # object to access MPI methods




class Simulation(object):
    '''
        Includes methods to run and control the simulation
    '''



    def __init__(self,conf,network):

        self.net = network
        self.conf = conf
            
        bionet_dir = os.path.dirname(bionet_io.__file__)  # path to package
        h.load_file(bionet_dir+'/advance.hoc')

        self.gids = self.net.graph.gids_on_rank   # returns dictionary of gid groups

        h.dt = self.conf["run"]["dt"]
        h.tstop = self.conf["run"]["tstop"]

        self.nsteps = int(round(h.tstop/h.dt))

        h.runStopAt = h.tstop
        h.steps_per_ms = 1/h.dt
        
        self.set_init_conditions()  # call to save state
        h.cvode.cache_efficient(1)
               
        h.pysim = self  # use this objref to be able to call postFadvance from proc advance in advance.hoc



    def set_init_conditions(self):

        '''
            Set up the initial conditions: either read from the h.SaveState or from config["condidtions"]
        '''

        pc.set_maxstep(10)
        h.stdinit()

        self.tstep = int(round(h.t/h.dt))
        self.tstep_start_block = self.tstep

        if self.conf["run"]["start_from_state"]==True:
            bionet_io.read_state()
            bionet_io.print2log0('Read the initial state saved at t_sim: %.2f ms' % (h.t))

        else:
            h.v_init = self.conf["conditions"]["v_init"]

            h.celsius = self.conf["conditions"]["celsius"]


                
    def set_recordings(self):

        if self.conf["run"]["calc_ecp"]: 
            self.set_ecp_recording()

        if not(self.conf["run"]["start_from_state"]): # if starting from a new initial state
            bionet_io.create_output_files(self.conf, self.gids);
    
        if self.conf["run"]["start_from_state"]: # if starting from a new initial state
            bionet_io.extend_output_files(self.gids)

        self.create_data_block()
        self.set_spike_recording()


        pc.barrier()


    def set_ecp_recording(self):

        self.mel = Electrode(self.conf)
        self.net.calc_seg_coords()              # use for computing the ECP
        
        for gid in self.gids['biophysical']:
            cell = self.net.cells[gid]
            self.mel.map_segs(gid,cell.seg_coords)

        h.cvode.use_fast_imem(1)   # make i_membrane_ a range variable
        self.fih1 = h.FInitializeHandler(0, self.net.set_ptr2im)


    def set_extra_stimulation(self):  # Fahimeh

        self.sel = StimXElectrode(self.conf)

        for gid in self.gids['biophysical']:
            cell = self.net.cells[gid]
            self.sel.set_transfer_resistance(gid, cell.seg_coords)

        self.fih = h.FInitializeHandler(0, self.net.set_ptr2e_extracellular)


    def attach_current_clamp(self):  # Fahimeh

        self.Ic = IClamp(self.conf)
        for gid in self.gids['biophysical']:
            cell = self.net.cells[gid]
            self.Ic.attach_current(cell)



    def create_data_block(self):


        nt_block = self.conf['run']['nsteps_block']
            
        self.data_block = {}
        self.data_block["tsave"] = round(h.t,3)
        
        if self.conf["run"]['calc_ecp']:
            nsites = self.mel.nsites
            self.data_block['ecp'] = np.empty((nt_block,nsites))

        self.data_block['cells'] = {}

        if self.conf["run"]["save_cell_vars"]:

            for gid in self.gids["save_vars"]:   # only includes gids on this rank

                self.data_block['cells'][gid] = {}        
                self.data_block['cells'][gid]['vm'] = np.zeros(nt_block)
                self.data_block['cells'][gid]['vext'] = np.zeros(nt_block)
                self.data_block['cells'][gid]['cai'] = np.zeros(nt_block)
                self.data_block['cells'][gid]['im'] = np.zeros(nt_block)
                self.data_block['cells'][gid]['EX'] = np.zeros(nt_block)

                if self.conf["run"]["calc_ecp"] and gid in self.gids['biophysical']: # then also create a dataset for the ecp
                    self.data_block['cells'][gid]['ecp'] = np.empty((nt_block,nsites))   # for extracellular potential


    def set_spike_recording(self):
        '''
            Set dictionary of hocVectors for spike recordings
        '''

        spikes = {}

        for gid in self.net.cells:
            tVec = h.Vector();    gidVec = h.Vector()
            pc.spike_record(gid,tVec,gidVec)
            spikes[gid] = tVec
            
        self.data_block["spikes"] = spikes

 
 
        
    def run(self):
        '''
        Run simulation using h.run if beginning from a blank state or with h.continuerun() if continuing from the saved state
        
        '''
        begin_time = time()
        self.start_time = h.startsw()
        pc.timeout(0) #
         
        pc.barrier() # wait for all hosts to get to this point
        bionet_io.print2log0('Running simulation until tstop: %.3f ms with the time step %.3f ms' % (self.conf["run"]['tstop'], self.conf["run"]['dt']))

        bionet_io.print2log0('Starting timestep: %d at t_sim: %.3f ms' % (self.tstep, h.t))
        bionet_io.print2log0('Block save every %d steps' % (self.conf["run"]['nsteps_block']))

        if self.conf["run"]["start_from_state"]:   h.continuerun(h.tstop)
        else:            h.run(h.tstop)        # <- runs simuation: works in parallel
                    
        pc.barrier() #  
        end_time = time()
        self.run_duration = end_time - begin_time

        bionet_io.print2log0('Simulation Duration %f!' % (self.run_duration))
        
    def report_load_balance(self):

        comptime = pc.step_time()
        
        print 'comptime: ', comptime,pc.allreduce(comptime, 1)
        avgcomp = pc.allreduce(comptime, 1)/pc.nhost()
        maxcomp = pc.allreduce(comptime, 2)
        bionet_io.print2log0('Maximum compute time is %g seconds.' % (maxcomp))
        bionet_io.print2log0('Approximate exchange time is %g seconds.' % (comptime - maxcomp))
        if (maxcomp != 0.0):
            bionet_io.print2log0('Load balance is %g.' % (avgcomp / maxcomp))


        
    def post_fadvance(self): 
        '''
        Runs after every execution of fadvance (see advance.hoc)
        Called after every time step to perform computation or save data.
        The initial condition tstep=0 is not being saved 
        '''


        self.tstep+=1

        tstep_block = self.tstep-self.tstep_start_block # time step within a block   

        self.data2block(tstep_block)

#    perform the operations below
        if (self.tstep % self.conf["run"]["nsteps_block"]==0) or self.tstep==self.nsteps: 

            bionet_io.print2log0('    step:%d t_sim:%.3f ms' % (self.tstep, h.t))
            self.tstep_end_block = self.tstep
           
            time_step_interval = (self.tstep_start_block,self.tstep_end_block)
            bionet_io.save_block2disk(self.conf, self.data_block, time_step_interval)  # block save data
            self.set_spike_recording()

            self.tstep_start_block = self.tstep   # starting point for the next block

            if self.conf["run"]["save_state"]:    
                bionet_io.save_state()





    def data2block(self,tstep_block):
        '''
        Save data to a memory block
            
        '''
        self.data_block["tsave"] = round(h.t,3)
        
#    save to block the ECP variable 
        if self.conf["run"]["calc_ecp"]:
 
            self.mel.clear_ecp_combined()
 
            for gid in self.gids['biophysical']: # compute ecp only from the biophysical cells

                cell = self.net.cells[gid]    
                im = cell.get_im()
                ecp = self.mel.get_ecp(gid,im)  # time consuming multiplication hides here
                self.mel.add_to_ecp_combined(ecp)

                # Fahimeh: scatter v_extracellular to e_extracellular
                if self.conf["run"]['extra_stim']:
                    # if self.tstep == 1 :
                    #     start = time()
                        self.sel.calculate_waveforms(self.tstep)
                        # end = time()
                        # print end - start
                        vext_vec = self.sel.get_vext(gid)
                        cell.set_e_extracellular(vext_vec)

                if self.conf['run']['save_cell_vars'] and gid in self.gids['save_vars'] :
                    cell_data_block = self.data_block['cells'][gid] 
                    cell_data_block['ecp'][tstep_block-1,:] = ecp
      
            self.data_block['ecp'][tstep_block-1,:] = self.mel.ecp_combined


        #    save to block intracellular variables


            if self.conf['run']['save_cell_vars']:
                for gid in list(set(self.gids['save_vars'])&set(self.gids['biophysical'])):

                    cell_data_block = self.data_block['cells'][gid]
                    cell = self.net.cells[gid]
                    cell_data_block['vm'][tstep_block-1] = cell.hobj.soma[0](0.5).v   # subtract 1 because indexes start at 0 while the time step starts at 1
                    if self.conf["run"]["extra_stim"]:
                        cell_data_block['vext'][tstep_block-1] = cell.hobj.soma[0](0.5).vext[0]
                        cell_data_block['EX'][tstep_block - 1] = cell.hobj.soma[0](0.5).e_extracellular
                        cell_data_block['im'][tstep_block-1] = cell.hobj.soma[0](0.5).i_membrane

                    # print  '{0:.30f}'.format(cell.hobj.soma[0](0.5).e_extracellular)
                                                      # ,
                    #                                       cell.hobj.soma[0](0.5).vext[0],
                    #                                   cell.hobj.soma[0](0.5).i_membrane,
                    #                                 cell.hobj.soma[0](0.5).i_membrane_)




    # def set_extra_stimulation(self): #Fahimeh
    #
    #     self.sel = StimXElectrode(self.conf)
    #
    #     for gid in self.gids['biophysical']:
    #         cell = self.net.cells[gid]
    #         self.sel.transfer_resistance(gid, cell.seg_coords)
    #         self.sel.get_vext(cell)
    #         self.sel.set_stimulation(cell)
