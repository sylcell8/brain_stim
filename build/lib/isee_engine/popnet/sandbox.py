from isee_engine.popnet import dipde
    
# "Model Construction" 
e_pop = dipde.InternalPopulation(v_min=-.03, v_max=.015, tau_m=.01, update_method='approx', dv=.0001, metadata={'model':'Excitatory'})
i_pop = dipde.InternalPopulation(v_min=-.03, v_max=.015, tau_m=.01, update_method='approx', dv=.0001, metadata={'model':'Inhibitory'})
bg_pop = dipde.ExternalPopulation(100, record=False, metadata={'model':'Background_100'})
population_list = [e_pop, i_pop, bg_pop]
connection_list = []

# Configure and run model:

network = dipde.Network(population_list, connection_list)

network_dict = network.to_dict()
for key, val in network_dict.items():
    print key, val