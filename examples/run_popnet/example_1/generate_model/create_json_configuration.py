import os
import json
from isee_engine.popnet import dipde
from isee_engine.popnet.configuration import Configuration

example_directory = '../'
configuration_file_name = os.path.join(example_directory, 'simulation_configuration.json')
node_table_file_name = 'node_table_dipde.csv'
model_table_file_name = 'model_table_dipde.csv'
checkpoint_file_name = 'checkpoint.json'
t0 = 0
tf = .1
dt = .0001
checkpoint_period = .5

c = Configuration(node_table=node_table_file_name,
                  model_table=model_table_file_name,
                  checkpoint_file_name = checkpoint_file_name,
                  checkpoint_period = checkpoint_period,
                  t0=t0,
                  tf=tf,
                  dt=dt)

c.to_json(save_file_name=configuration_file_name)
