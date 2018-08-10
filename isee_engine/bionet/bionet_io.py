import pandas as pd
import time, datetime
import os,sys
import shutil
import json
import numpy as np
from isee_engine.bionet import nrn
import logging
import isee_engine.bionet.config as config



from neuron import h

pc = h.ParallelContext()    # object to access MPI methods




def load_json(fullpath):
    '''
    Load a json file
    Parameters:
    full_path: string
                path to the file name to be loaded
    '''

    try:    
        with open(fullpath, 'r') as f: data=json.load(f)
    except IOError:
        print2log0("ERROR: cannot open %s" % fullpath)
        nrn.quit_execution()

    return data

import h5py

def load_h5(file_name):

    '''
    load ij connections

    Parameters
    ----------
    file_name: string
        full path to h5 file
    
    
    Returns
    -------
    data__handle: file handle

    '''    


    try:    
        data_handle = h5py.File(file_name,'r')
    except IOError:
        print2log0("ERROR: cannot open %s" % file_name)
        nrn.quit_execution()

    
    return data_handle


def load_csv(fullpath):
    '''
    Load a csv file
    Parameters:
    full_path: string
                path to the file name to be loaded
    '''

    try:    
        data = pd.read_csv(fullpath, sep=' ')
    except IOError:
        print2log0("ERROR: cannot open %s" % fullpath)
        nrn.quit_execution()
        
    return data



def create_log(conf):

    logging.basicConfig(filename=conf["output"]["log"],level=logging.DEBUG)


    now = datetime.datetime.now()


    print2log0('The log created on %02d/%02d/%02d at %02d:%02d:%02d' % (now.year, now.month, now.day, now.hour, now.minute, now.second)) 

    




def print2log(string):

    '''
    Print statements to the log file from all processors
    '''        
    delta_t = time.clock()
    full_string = string+', t_wall: %s s' %(str(delta_t))
    logging.info(full_string) 



    

def print2log0(string): 
    '''
    Print from rank=0 only

    '''

#    CAUTION: NEURON's warning will not be save in either RUN_LOG or the log file created by the PBS. 
#    To catch possible NEURON warnings, you need to use shell redirection, e.g.: $ python foo.py > file
    
    if int(pc.id())==0:

        delta_t = time.clock()
        full_string = string+' -- t_wall: %s s' %(str(delta_t))
        print full_string   # echo on the screen
        logging.info(full_string) 



    
def copy_config(conf): # copy config to output directory
    
    
    fullpath = "/".join([conf["manifest"]["$RUN_DIR"],conf['config_file_name']])

    print fullpath
    shutil.copy(fullpath,conf["manifest"]["$OUTPUT_DIR"])

    print2log0('Config file: '+conf['config_file_name'])
    




def make_output_dirs(conf):

    if os.path.exists(conf["manifest"]["$OUTPUT_DIR"]):

        if conf["run"]['overwrite_output_dir']==True:
            shutil.rmtree(conf["manifest"]["$OUTPUT_DIR"])
            print 'Overwriting the output directory %s:' %(conf["manifest"]["$OUTPUT_DIR"]) # must print to stdout because the log file is not created yet
        else:
            print 'ERROR: Directory already exists'
            print "To overwrite existing output_dir set 'overwrite_output_dir': True"
            nrn.quit_execution()

    
    os.makedirs(conf["manifest"]["$OUTPUT_DIR"])
    os.makedirs(conf["output"]["cell_vars_dir"])
    os.makedirs(conf["output"]["state_dir"])
    os.makedirs(conf["output"]["electrodes_dir"])



def extend_output_files(gids):

#TODO: resize the files when running from an existing state
    
    pass

def create_output_files(conf,gids):


    if conf["run"]["calc_ecp"]: # creat single file for ecp from all contributing cells
        create_ecp_file(conf)

    if conf["run"]["save_cell_vars"]:
        create_cell_vars_files(conf,gids)

    if conf["run"]["extra_stim"]:
        copy_electrode_files(conf)
        copy_cell_files(conf)
                
    create_spike_file(conf,gids) # a single file including all gids


def copy_electrode_files(conf):
    '''
    Copy electrode data to output directory
    '''
    el_dir = conf["output"]["electrodes_dir"]
    pos_path = conf["extracellular_stimelectrode"]["position"]
    pos_df = pd.read_csv(pos_path, sep=' ')
    mesh_files = pos_df["electrode_mesh_file"]

    shutil.copy(pos_path, el_dir)

    for f in mesh_files:
        mesh_path = "/".join([conf["manifest"]["$STIM_DIR"], f])
        shutil.copy(mesh_path, el_dir)

def copy_cell_files(conf):
    '''
    Copy electrode data to output directory
    '''
    out_dir = conf["manifest"]["$OUTPUT_DIR"]
    file_path = conf["internal"]["cells"]

    shutil.copy(file_path, out_dir)

def create_ecp_file(conf):

    '''
        a single ecp file for the entire network
        
    '''
    print2log0('Will save time series of the ECP!')

    dt = conf["run"]["dt"]
    tstop = conf["run"]["tstop"]

    nsteps = int(round(tstop/dt))
    nsites =  conf['run']['nsites']

    ofname  = conf["output"]["extra_cell_vars"]
    if int(pc.id())==0: # creat single file for ecp from all contributing cells
    
#         f5 = h5py.File(conf["output"]["extra_cell_vars"],libver='latest')
#         f5.create_dataset('ecp',(nsteps,nsites),maxshape=(None,nsites),chunks=True)
#         f5.attrs['dt']=dt; 
#         f5.attrs['tstart']=0.0
#         f5.attrs['tstop']=tstop

        with h5py.File(ofname,'w') as f5:
            f5.create_dataset('ecp',(nsteps,nsites),maxshape=(None,nsites),chunks=True)
            f5.attrs['dt']=dt; 
            f5.attrs['tstart']=0.0
            f5.attrs['tstop']=tstop
            

    pc.barrier()


def create_cell_vars_files(conf,gids):

    '''
        create 1 hfd5 files per gid
    '''

    print2log0('Will save time series of individual cells')

    dt = conf["run"]["dt"]
    tstop = conf["run"]["tstop"]

    nsteps = int(round(tstop/dt))

    
    for gid in gids["save_vars"]:
        
        ofname = conf["output"]["cell_vars_dir"]+'/%d.h5' % (gid)
        with h5py.File(ofname,'w') as h5:

            h5.attrs['dt']=dt; 
            h5.attrs['tstart']=0.0
            h5.attrs['tstop']=tstop
     
            h5.create_dataset('vm',(nsteps,),maxshape=(None,),chunks=True, dtype=np.float64)
            h5.create_dataset('cai',(nsteps,),maxshape=(None,),chunks=True, dtype=np.float64)
            h5.create_dataset('im', (nsteps,), maxshape=(None,), chunks=True, dtype=np.float64)
            # if conf["run"]["extra_stim"]:
            h5.create_dataset('vext', (nsteps,), maxshape=(None,), chunks=True, dtype=np.float64)
            h5.create_dataset('EX', (nsteps,), maxshape=(None,), chunks=True, dtype=np.float64)

            h5.create_dataset('spikes',(0,),maxshape=(None,), chunks=True, dtype=np.float64)
     
            if conf["run"]["calc_ecp"]: # then also create a dataset for the ecp
                nsites =  conf['run']['nsites']
                h5.create_dataset('ecp',(nsteps,nsites),maxshape=(None,nsites),chunks=True)
    


def create_spike_file(conf,gids_on_rank):

    '''
        create a single hfd5 files for all gids
    '''

    ofname = conf["output"]["spikes_h5"] 

    tstop = conf["run"]["tstop"]


    ranks = range(int(pc.nhost()))

    if int(pc.id())==0:     #create h5 file 
        with h5py.File(ofname,'w') as h5:
            h5.attrs['tstart']=0.0
            h5.attrs['tstop']=tstop

    pc.barrier()
        

    for rank in ranks:
        if rank==int(pc.id()):
            with h5py.File(ofname,'a') as h5:
                for gid in gids_on_rank["all"]:
                    h5.create_dataset('%d' %gid,(0,), maxshape=(None,), chunks=True)
        pc.barrier()


    if int(pc.id())==0:     #create ascii file 
        ofname = conf["output"]["spikes_ascii"]
        f = open(ofname,'w')    # create ascii file
        f.close()
 
    pc.barrier()



def get_spike_trains_handle(file_name,trial_name):


    f5  = load_h5(file_name)

    spike_trains_handle = f5['processing/%s/spike_train' % trial_name] 

    return spike_trains_handle


def setup_work_dir(conf):


    if conf["run"]["start_from_state"]==True: # starting from a previously saved state

        try:
            assert os.path.exists(conf["manifest"]["$OUTPUT_DIR"])
            print2log0('Will run simulation from a previously saved state...')
        except:
            print 'ERROR: directory with the initial state does not exist'
            nrn.quit_execution()

    elif conf["run"]["start_from_state"]==False: # starting from a new state 

        if int(pc.id())==0:
    
            make_output_dirs(conf)
            create_log(conf)    
            config.copy(conf)
            config.print_resolved(conf)

        pc.barrier()
        





def save_block2disk(conf,data_block,time_step_interval):
    '''
    save data in blocks to hdf5 
    '''

    # save_ecp(conf,data_block,time_step_interval)
    save_cell_vars(conf,data_block,time_step_interval)
    save_spikes2h5(conf,data_block)
    save_spikes2ascii(conf,data_block)
    

def save_spikes2h5(conf,data_block):

    '''
    Save spikes to h5 file: each cell has a separate dataset.
    ''' 
    spikes = data_block["spikes"]

    ofname = conf["output"]["spikes_h5"] 

    ranks = xrange(int(pc.nhost()))

    for rank in ranks:  # iterate over the ranks
        if rank==int(pc.id()): # wait until finished with a particular rank 
            with h5py.File(ofname,'a') as h5:
                for gid in spikes:                          # save spikes of all gids on this rank
                    nspikes_saved = h5[str(gid)].shape[0]   # find number of spikes
                    nspikes_add = len(spikes[gid])          # find number of spikes to add
                    nspikes = nspikes_saved+nspikes_add     # total number of spikes
                    h5[str(gid)].resize((nspikes,))         # resize the dataset
                    h5[str(gid)][nspikes_saved:nspikes] = np.array(spikes[gid]); # save hocVector as a numpy arrray

        pc.barrier()    # move on to next rank





def save_ecp(conf, data_block, time_step_interval):

    '''
    Save ECP from each rank to disk into a single file
    '''

    itstart,itend = time_step_interval

    ofname = conf["output"]["extra_cell_vars"]

    if conf["run"]['calc_ecp']:

        ranks = xrange(int(pc.nhost()))
        for rank in ranks:              # iterate over the ranks
            if rank==int(pc.id()):      # wait until finished with a particular rank 
                with h5py.File(ofname,'a') as f5:
                    f5["ecp"][itstart:itend,:] += data_block['ecp'][0:itend-itstart,:];
                    f5.attrs["tsave"] = data_block["tsave"] # update tsave

#                 f5 = h5py.File(ofname, 'a', libver='latest')
#                 f5["ecp"][itstart:itend,:] += data_block['ecp'][0:itend-itstart,:];
#                 f5.attrs["tsave"] = data_block["tsave"] # update tsave
#                 f5.close()

            pc.barrier()    # move on to next rank



#def save_cell_vars(data_block, time_step_interval, ofpat): # David's suggestion

def save_cell_vars(conf,data_block, time_step_interval): 

    '''
        save to disk with one file per gid
    '''

    itstart,itend = time_step_interval
    
    #ofpat = os.path.join(prm.get_path(prm.conf["output"]["cell_vars_dir"]), "%d") 
    
    for gid,cell_data_block in data_block['cells'].items():

        ofname = conf["output"]["cell_vars_dir"]+'/%d.h5' % (gid)#        ofname = ofpat % gid # David's suggestion


        with h5py.File(ofname,'a') as h5:

            h5.attrs["tsave"] = data_block["tsave"] # update tsave

            h5["vm"][itstart:itend] = cell_data_block['vm'][0:itend-itstart];
            cell_data_block['vm'][:] = 0.0
    
            # h5["cai"][itstart:itend] = cell_data_block['cai'][0:itend-itstart];
            # cell_data_block['cai'][:] = 0.0

            h5["im"][itstart:itend] = cell_data_block['im'][0:itend-itstart];
            cell_data_block['im'][:] = 0.0

            h5["vext"][itstart:itend] = cell_data_block['vext'][0:itend-itstart];
            cell_data_block['vext'][:] = 0.0

            # h5["EX"][itstart:itend] = cell_data_block['EX'][0:itend-itstart];
            # cell_data_block['EX'][:] = 0.0

            # if "ecp" in cell_data_block.keys():
            #     h5["ecp"][itstart:itend,:] = cell_data_block['ecp'][0:itend-itstart,:];
            #     cell_data_block['ecp'][:] = 0.0

            spikes = data_block["spikes"]
            nspikes_saved = h5["spikes"].shape[0]   # find number of spikes
            nspikes_add = len(spikes[gid])     # find number of spikes to add
            nspikes = nspikes_saved+nspikes_add     # total number of spikes
            h5["spikes"].resize((nspikes,))         # resize the dataset
            h5["spikes"][nspikes_saved:nspikes] = np.array(spikes[gid]); # save hocVector as a numpy arrray





def save_spikes2ascii(conf,data_block):

    spikes = data_block["spikes"]
    '''
    Save spikes to ascii file as tuples (t,gid). 
    ''' 
    ofname = conf["output"]["spikes_ascii"]

    ranks = xrange(int(pc.nhost()))
    for rank in ranks:
        if rank==int(pc.id()):
            f = open(ofname,'a')
            for gid in spikes:
                tVec = spikes[gid]
                for t in tVec: f.write('%.3f %d\n' %(t, gid))
            f.close()
        pc.barrier()



def save_state(conf):

    state = h.SaveState()
    state.save()

    state_dir = conf["output"]["state_dir"]
    f = h.File(state_dir+'/state_rank-%d' % (int(pc.id())))
    state.fwrite(f, 0)
    rlist = h.List('Random')
    for r_tmp in rlist:
        f.printf('%g\n', r_tmp.seq())
    f.close()


def read_state(conf):

    state_dir = conf["output"]["state_dir"]
    
    state = h.SaveState()
    f = h.File(state_dir+'/state_rank-%d' % (int(pc.id())))
    state.fread(f, 0)
    state.restore()
    rlist = h.List('Random')
    for r_tmp in rlist:
        r_tmp.seq(f.scanvar())
    f.close()
    


