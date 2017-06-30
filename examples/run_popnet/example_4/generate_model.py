import matplotlib.pyplot as plt
from isee_engine.popnet import dipde

# Create nodes:
ext_pop = dipde.ExternalPopulation(100, record=False, metadata={'model':'Background_100'})
int_pop = dipde.InternalPopulation(v_min=-.03, 
                                   v_max=.015, 
                                   tau_m=.01, 
                                   update_method='approx', 
                                   dv=.0001, 
                                   metadata={'model':'Inhibitory'})

# Create edges:
conn = dipde.Connection(ext_pop, int_pop, 1, weights=.005, delays=0.0)

# Configure model:
simulation_configuration = dipde.SimulationConfiguration(dt=.0001, 
                                                         tf=.1, 
                                                         t0=0,
                                                         checkpoint_file_name = 'checkpoint.json', 
                                                         checkpoint_period=.5)
network = dipde.Network(population_list=[int_pop, ext_pop], connection_list=[conn]).to_target_network()

# Run simunation
simulation = dipde.Simulation(network=network, simulation_configuration=simulation_configuration)
simulation.run()

network.population_list[0].plot()
plt.show()