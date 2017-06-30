import matplotlib.pyplot as plt
from isee_engine.popnet.configuration import Configuration
from isee_engine.popnet import dipde
from isee_engine.popnet.checkpointsimulation import CheckpointSimulation
import threading
import time
import logging
import scipy.io as sio

# Settings:
logging.disable(logging.DEBUG)
configuration_file_name = './simulation_configuration.json'
configuration = Configuration.load(configuration_file_name)
simulation = configuration.get_simulation()

# background_list = []
# for p in simulation.network.population_list:
#     if p.metadata['model'] == 'Inhibitory':
#         pi = p
#     elif p.metadata['model'] == 'Excitatory':
#         pe = p
#     else:
#         p.record = True
#         background_list.append(p)
#         
# for bp in background_list:
#  
#     curr_c = dipde.Connection(bp, pi, 10./len(background_list), weights=.005, delays=0.0)
#     curr_c.simulation = simulation.network
#     simulation.network.connection_list.append(curr_c)
#      
#     curr_c = dipde.Connection(bp, pe, 10./len(background_list), weights=.005, delays=0.0)
#     curr_c.simulation = simulation.network
#     simulation.network.connection_list.append(curr_c)
#     
# curr_c = dipde.Connection(pi, pe, 3, weights=-.005, delays=0.0)
# curr_c.simulation = simulation.network
# simulation.network.connection_list.append(curr_c)


simulation.run()

t = pi.t_record
firing_rate_i = pi.firing_rate_record
firing_rate_e = pe.firing_rate_record

file_name = '/data/mat/iSee_temp_shared/council2016/dipde_firing_rate_v2'
sio.savemat(file_name, {'t':t, 'firing_rate_i':firing_rate_i, 'firing_rate_e':firing_rate_e})

 
fig, ax = plt.subplots()
pi.plot(ax=ax, show=False, c='r')
pe.plot(ax=ax, show=False, c='r')
for bp in background_list:
    bp.plot(ax=ax, show=False, c='b')
plt.show()






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

