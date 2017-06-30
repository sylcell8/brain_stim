from isee_engine.popnet.configuration import Configuration
from isee_engine.popnet import dipde
from isee_engine.popnet.checkpointsimulation import CheckpointSimulation
import threading
import time
import logging

# Settings:
# logging.disable(logging.INFO)
configuration_file_name = './simulation_configuration.json'
configuration = Configuration.load(configuration_file_name)
simulation = configuration.get_simulation()
simulation.run()

# Load and run, no checkpointing:




# # Load and run, with checkpointing:
# simulation = configuration.get_checkpoint_simulation()
# simulation.run()

        
# def f(network):
#     print network.t
        
# s = CheckpointSimulation(simulation, checkpoint_period, checkpoint_file_name)

# s.run()

# from isee_engine.popnet import dipde
# from isee_engine.popnet.from_csv import create_instance
# import json
#  
# n_dict = json.load(open('checkpoint.json', 'r'))
# print n_dict.keys()
# s = create_instance(json.load(open('checkpoint.json', 'r')))
# print s
# print s.simulation_configuration.t0
# print s.simulation_configuration.tf
# print s.simulation_configuration.dt
# # print s.population_list[0].t_record
# # print s.population_list[0].t_record[-1]
# s.run()
# print s.network.population_list[0].t_record[-210:-195]
# print s.network.population_list[0].plot()
# import matplotlib.pyplot as plt
# plt.show()

# s.keys()

# dipde.Simulation.load_simulation('checkpoint.json') 

# s.start()
# simulation.run()
# 
# 
# simulation. 

