from isee_engine.popnet.utilities import create_nwb_server_file_path
from isee_engine.popnet import dipde

ExternalPopulation = dipde.ExternalPopulation

class NWBExternalPopulation(ExternalPopulation):
    
    
    def __init__(self, nwb_file_name, nwb_path, rank=0,record=False, firing_rate_record=[], t_record=[], metadata={}, **kwargs):

        self.nwb_file_name = nwb_file_name
        self.nwb_path = nwb_path
        
        firing_rate = create_nwb_server_file_path(nwb_file_name, nwb_path)
        super(NWBExternalPopulation, self).__init__(firing_rate, rank=rank,record=record, firing_rate_record=firing_rate_record, t_record=t_record, metadata=metadata, **kwargs)
    
    @property
    def module_name(self):
        return __name__
        
    def to_dict(self):
        
        data_dict = super(NWBExternalPopulation, self).to_dict()
        
        data_dict['nwb_file_name'] = self.nwb_file_name
        data_dict['nwb_path'] = self.nwb_path
        
        return data_dict
        
if __name__ == "__main__":

    nwb_file_name = '/data/mat/iSee_temp_shared/external_inputs/anton_flash_example/anton_flash_example.nwb'
    nwb_path = '/acquisition/firing_rate/0'
    b1 = NWBExternalPopulation(nwb_file_name, nwb_path)
    print b1.to_dict()

#         
#     nwb_file_name = '/data/mat/iSee_temp_shared/external_inputs/anton_flash_example/anton_flash_example.nwb'
#     nwb_path = '/acquisition/firing_rate/0'
#     
#     # Settings:
#     t0 = 0.
#     dt = .0001
#     dv = .0001
#     tf = 3
#     update_method = 'approx'
#     tol = 1e-14
#     
#     
#     b1 = NWBExternalPopulation(nwb_file_name, nwb_path)
#     i1 = dipde.InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, tol=tol)
#     b1_i1 = dipde.Connection(b1, i1, 10, weights=.005, delays=0.0)
#     network = dipde.Network([b1, i1], [b1_i1])
#     network.run(dt=dt, tf=tf, t0=t0)
    
