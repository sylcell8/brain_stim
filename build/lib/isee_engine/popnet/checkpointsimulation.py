from isee_engine.popnet import dipde
import threading
import time
import logging
logger = logging.getLogger(__name__)

class CheckpointSimulation(object):
    
    def __init__(self, simulation, checkpoint_period=None, checkpoint_file_name=None):
        
        self.simulation = simulation
        self.simulation.network.update_callback = self._simulation_update_callback
        self.thread = threading.Thread(target=self.run_checkpoint_thread)
        self.thread.daemon = True
        self.checkpoint_period = checkpoint_period
        self.checkpoint_file_name = checkpoint_file_name
        
    def run_checkpoint_thread(self):
        while True:
            time.sleep(self.checkpoint_period)
            
            # Request pause
            self.pause = True 
            while self._network_trapped_at_callback == False:
                time.sleep(.1) 
            
            # Network is at update_callback, safe to write:
            checkpoint_simulation_configuration = dipde.SimulationConfiguration(t0=self.simulation.network.t, 
                                                                                tf=self.simulation.simulation_configuration.tf,
                                                                                dt=self.simulation.simulation_configuration.dt,)
            checkpoint_simulation = dipde.Simulation(simulation_configuration=checkpoint_simulation_configuration,
                                                     network = self.simulation.network)
            checkpoint_simulation.to_json(fh=open('checkpoint.json', 'w'))
            logger.info('Checkpoint (%s): %s' % (self.checkpoint_file_name, self.simulation.network.t))
            
            # Release from pause
            self.pause = False

            
    def _simulation_update_callback(self, network):
        self._network_trapped_at_callback = True
        while self.pause == True:
            time.sleep(.1)
        self._network_trapped_at_callback = False
            
    def run(self):
        self.pause = False
        if not (self.checkpoint_file_name is None or self.checkpoint_period is None): 
            self.thread.start()
        self.simulation.run()