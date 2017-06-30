import json
import pandas as pd

from isee_engine.popnet import dipde

black_list = ['firing_rate_record', 
              'initial_firing_rate', 
              'metadata', 
              't_record']

json_list = ['p0', 'tau_m']

def to_dict(p):
    
    return_dict = {}
    p_dict = p.to_dict()

    for key, val in p_dict['metadata'].items():
        return_dict[key] = val
    
    for key, val in p_dict.items():
        if key not in black_list:
            if key in json_list:
                val = json.dumps(val)
            return_dict[key] = val
            
    return return_dict



e_pop = dipde.InternalPopulation(v_min=-.03, v_max=.015, tau_m=.01, update_method='approx', dv=.0001, metadata={'model':'Excitatory'})
i_pop = dipde.InternalPopulation(v_min=-.03, v_max=.015, tau_m=.01, update_method='approx', dv=.0001, metadata={'model':'Inhibitory'})
bg_pop = dipde.ExternalPopulation(100, record=False, metadata={'model':'Background'})

model_dict = {}
for p in [e_pop, i_pop]:
    for key, val in to_dict(p).items():
        model_dict.setdefault(key, []).append(val)
df_int = pd.DataFrame(model_dict)

model_dict = {}
for p in [bg_pop]:
    for key, val in to_dict(p).items():
        model_dict.setdefault(key, []).append(val)
df_ext = pd.DataFrame(model_dict)

df = pd.merge(df_ext, df_int, how='outer')



def reorder(frame, var):
    varlist = [w for w in frame.columns if w not in var]
    return frame[var+varlist]

df = reorder(df, ['model', 'class', 'module'])

df.to_csv('../model_table_dipde.csv', index=False, sep=' ', na_rep='None')

import pandas as pd
import itertools

data_dict = {}
for gid, (model, layer) in enumerate(itertools.product(['Excitatory', 'Inhibitory', 'Background'], ['2/3', '4', '5', '6'])):
    data_dict.setdefault('model', []).append(model)
    data_dict.setdefault('layer', []).append(layer)
    data_dict.setdefault('id', []).append(gid)


df = pd.DataFrame(data_dict)
df = reorder(df, ['id', 'model', 'layer'])

df.to_csv('../node_table_dipde.csv', index=False, sep=' ', na_rep='None')
    
    
