import os
from isee_engine.popnet.configuration import Configuration
import itertools
import pandas as pd
from isee_engine.popnet import dipde
from isee_engine.popnet.io import population_list_to_csv, df_to_csv
from isee_engine.popnet.utilities import reorder_columns_in_frame, population_to_dict_for_dataframe
from isee_engine.popnet.nwbexternalpopulation import NWBExternalPopulation

configuration_file_name = 'simulation_configuration.json'
checkpoint_file_name = 'checkpoint.json'
nwb_input_file_name = '/data/mat/iSee_temp_shared/external_inputs/anton_flash_example/anton_flash_example.nwb'
model_table_file_name = 'model_table_dipde.csv'
node_table_file_name = 'node_table_dipde.csv'
t0 = 0
tf = .1
dt = .0001
checkpoint_period = .5

e_pop = dipde.InternalPopulation(v_min=-.03, v_max=.015, tau_m=.01, update_method='approx', dv=.0001, metadata={'model':'Excitatory'})
i_pop = dipde.InternalPopulation(v_min=-.03, v_max=.015, tau_m=.01, update_method='approx', dv=.0001, metadata={'model':'Inhibitory'})
bg_pop = NWBExternalPopulation(nwb_input_file_name, '/acquisition/firing_rate/0', metadata={'model':'Background'})
bg_pop_2 = dipde.ExternalPopulation(100, record=False, metadata={'model':'Background_100'})
population_list = [e_pop, i_pop, bg_pop_2, bg_pop]


# Create model csv file:
population_list_to_csv(population_list, model_table_file_name)

# Create node dict:
data_dict = {}
for gid, (model, layer) in enumerate(itertools.product(['Excitatory', 'Inhibitory', 'Background'], ['2/3', '4', '5', '6'])):
    data_dict.setdefault('model', []).append(model)
    data_dict.setdefault('layer', []).append(layer)
    data_dict.setdefault('id', []).append(gid)

# for key, val in data_dict.items():
#     print key, val

# Convert to data frame and save:
df = pd.DataFrame(data_dict)
df = reorder_columns_in_frame(df, ['id', 'model', 'layer'])
df_to_csv(df, node_table_file_name)


# Create configuration file
Configuration(node_table=node_table_file_name,
              model_table=model_table_file_name,
              checkpoint_file_name = checkpoint_file_name,
              checkpoint_period = checkpoint_period,
              t0=t0,
              tf=tf,
              dt=dt).to_json(save_file_name=configuration_file_name)

from isee_engine.popnet.utilities import list_of_dicts_to_dict_of_lists

print list_of_dicts_to_dict_of_lists([{'a':1, 'b':5}, {'a':2, 'b':10, 'c':1}])
    
    
