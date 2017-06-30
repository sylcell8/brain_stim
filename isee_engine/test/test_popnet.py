import json
import isee_engine
from isee_engine.popnet.configuration import Configuration 

def test_configuration():

    configuration = Configuration(node_table=None,
                                  model_table=None,
                                  t0=0,
                                  tf=.01,
                                  dt=.0001)
    
    # Test json serialization:
    s = configuration.to_json()
    
    # Test loader:
    Configuration(**json.loads(s))
    
def test_mesoscale_connectivity():
    
    from isee_engine.popnet.utilities import get_mesoscale_connectivity_dict
    
    nature_data = get_mesoscale_connectivity_dict()
    
    assert nature_data['W', 'ipsi', 'LGd', 'VISp'] == 7.53731563
    assert nature_data['W', 'ipsi', 'VISp', 'LGd'] == 0.151813329
    
if __name__ == '__main__':                                            # pragma: no cover
    test_configuration()                                              # pragma: no cover
    test_mesoscale_connectivity()                                     # pragma: no cover  