import matplotlib.pyplot as plt
import numpy as np
import os
from isee_engine.popnet.configuration import Configuration
import itertools
import pandas as pd
from isee_engine.popnet import dipde
from isee_engine.popnet.io import population_list_to_csv, df_to_csv
from isee_engine.popnet.utilities import reorder_columns_in_frame, population_to_dict_for_dataframe
from isee_engine.popnet.nwbexternalpopulation import NWBExternalPopulation

configuration_file_name = 'simulation_configuration.json'
nwb_input_file_name = '/data/mat/iSee_temp_shared/external_inputs/anton_TouchOfEvil_frames_3600_to_3750_example/anton_TouchOfEvil_frames_3600_to_3750.nwb'
model_table_file_name = 'model_table_dipde.csv'
node_table_file_name = 'node_table_dipde.csv'
t0 = 0
tf = .2
dt = .0001

e_pop = dipde.InternalPopulation(v_min=-.03, v_max=.01, tau_m=.025, update_method='approx', dv=.0001, metadata={'model':'Excitatory'})
i_pop = dipde.InternalPopulation(v_min=-.03, v_max=.01, tau_m=.025, update_method='approx', dv=.0001, metadata={'model':'Inhibitory'})

population_list = [e_pop, i_pop]
for ii in np.arange(0,9000,500):
    curr_bg_pop = NWBExternalPopulation(nwb_input_file_name, '/acquisition/firing_rate/%s' % ii, metadata={'model':'Background_%s' % ii})
    population_list.append(curr_bg_pop)

# Create model csv file:
population_list_to_csv(population_list, model_table_file_name)

# Create node dict:
data_dict = {}
for gid, p in enumerate(population_list):
    model = p.metadata['model']
    data_dict.setdefault('model', []).append(model)
    data_dict.setdefault('id', []).append(gid)

# Convert to data frame and save:
df = pd.DataFrame(data_dict)
df = reorder_columns_in_frame(df, ['id', 'model'])
df_to_csv(df, node_table_file_name)

# Create configuration file
Configuration(node_table=node_table_file_name,
              model_table=model_table_file_name,
              t0=t0,
              tf=tf,
              dt=dt).to_json(save_file_name=configuration_file_name)


    
    
