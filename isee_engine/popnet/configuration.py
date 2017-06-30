import json
from isee_engine.popnet import dipde
from isee_engine.popnet.checkpointsimulation import CheckpointSimulation
from isee_engine.popnet.io import create_population_list
import pandas as pd

class Configuration(object):
    """Popnet configuration class
        
        This class organizes all the settings necessary to configure a popnet simulation.
        
        Parameters
        ----------
        node_table: pandas DataFrame
            Table describing the nodes of the simulation
        model_table: pandas DataFrame
            Table describing the models that can be instated at the nodes
        t0: float
            Simulation start time 
        tf: float
            Simulation end time
        dt: float
            Simulation start time
    """
    
    configuration_element_list = ['node_table', 'model_table', 't0', 'tf', 'dt', 'checkpoint_period', 'checkpoint_file_name']
    configuration_default = {'checkpoint_period':None, 
                             'checkpoint_file_name':None}
    
    def __init__(self, **kwargs):
        
        for key in Configuration.configuration_element_list:
            if key in kwargs:
                setattr(self, key, kwargs[key])
            else:
                setattr(self, key, Configuration.configuration_default[key])
                                          
        
    def to_dict(self):
        '''Serialize configuration to dictionary.'''
        data_dict = {}
        for key in Configuration.configuration_element_list:
            data_dict[key] = getattr(self, key)
            
        return data_dict

    def to_json(self, save_file_name=None, **kwargs):
        '''Serialize configuration to json.'''
        if save_file_name is None:
            return json.dumps(self.to_dict(), indent=kwargs.get('indent',2))
        else:
            json.dump(self.to_dict(), open(save_file_name, 'w'), indent=kwargs.get('indent',2))
            
    def get_simulation_configuration(self):
        '''Get dipde SimulationConfiguration object.'''
        
        simulation_configuration = dipde.SimulationConfiguration(dt=self.dt,
                                                                 tf=self.tf,
                                                                 t0=self.t0)
        return simulation_configuration
    
    def get_node_list(self):
        '''Get list of dipde InternalPopulations and ExternalPopulations.'''

        node_table = pd.read_csv(self.node_table, sep=' ', na_values='None')
        model_table = pd.read_csv(self.model_table, sep=' ', na_values='None')
        return create_population_list(node_table, model_table)

    def get_connection_list(self):
        '''Get list of dipde Connections.'''
        return []

    def get_network(self):
        '''Get dipde Network.'''
        
        node_list = self.get_node_list()
        connection_list = self.get_connection_list()
        return dipde.Network(node_list, connection_list)
    
    def get_simulation(self):
        '''Get dipde Simulation.'''

        network = self.get_network()
        simulation_configuration = self.get_simulation_configuration()
        simulation = dipde.Simulation(simulation_configuration=simulation_configuration, network=network)
        
        if (self.checkpoint_period is None) or (self.checkpoint_file_name is None):
            return simulation
        else:
            return CheckpointSimulation(simulation, self.checkpoint_period, self.checkpoint_file_name)
        
    @staticmethod
    def load(configuration_file_name):
        '''Load Configuration from json serialization'''
        configuration = Configuration(**Configuration.from_json(configuration_file_name))
        return configuration
    
    @staticmethod
    def load_simulation(configuration_file_name):
        '''Load dipde Simulation from json serialized Configuration'''
        configuration = Configuration.load(configuration_file_name)
        return configuration.get_simulation()
    
    @staticmethod
    def from_json(load_file_name):
        '''Load Configuration from json serializeation '''
        return json.load(open(load_file_name, 'r'))
        
    
if __name__ == "__main__":
    
    node_table_file_name = '/data/mat/nicholasc/isee_engine/examples/run_popnet/node_table_dipde.csv'
    model_table_file_name = '/data/mat/nicholasc/isee_engine/examples/run_popnet/model_table_dipde.csv'
    config_file_name = '/data/mat/nicholasc/isee_engine/examples/run_popnet/simulation_configuration.json'
    t0 = 0
    tf = .1
    dt = .0001
    
    c = Configuration(node_table=node_table_file_name,
                      model_table=model_table_file_name,
                      t0=t0,
                      tf=tf,
                      dt=dt)

    c_str = c.to_json()
    Configuration(**Configuration.from_json(config_file_name))
    
