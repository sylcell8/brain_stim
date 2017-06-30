import math
import importlib
import pandas as pd
from isee_engine import UnknownModelError
from utilities import population_to_dict_for_dataframe

def population_list_to_dataframe(population_list):
    df = pd.DataFrame({'_tmp':[None]})
    for p in population_list:
        model_dict = {'_tmp':[None]}
        for key, val in population_to_dict_for_dataframe(p).items():
            model_dict.setdefault(key, []).append(val)
        df_tmp = pd.DataFrame(model_dict)
        
        df = pd.merge(df, df_tmp, how='outer')
    df.drop('_tmp', inplace=True, axis=1)
    return df

def df_to_csv(df, save_file_name, index=False, sep=' ', na_rep='None'):
    df.to_csv(save_file_name, index=index, sep=sep, na_rep=na_rep)

def population_list_to_csv(population_list, save_file_name):
    df = population_list_to_dataframe(population_list)
    df_to_csv(df, save_file_name)

def create_instance(data_dict):
    '''Helper function to create an object from a dictionary containing:
    
    "module": The name of the module containing the class
    "class": The name of the class to be used to create the object
    '''
    
    curr_module, curr_class = data_dict.pop('module'), data_dict.pop('class')
    curr_instance = getattr(importlib.import_module(curr_module), curr_class)(**data_dict)
    
    return curr_instance

def assert_model_known(model, model_dict):
    """Test if a model in in the model_dict; if not, raise UnknownModelError"""
    
    try:
        assert model in model_dict
    except:
        raise UnknownModelError(model)

def create_population_list(node_table, model_table):
    """Create a population list from the node and model pandas tables"""

    model_dict = {}
    for row in model_table.iterrows():
        model = row[1].to_dict()
        model_dict[model.pop('model')] = model
    
    population_list = []
    for row in node_table.iterrows():
        node = row[1].to_dict()
        model = node.pop('model')

        # Check if model type in model dict:
        assert_model_known(model, model_dict)
        
        # Clean up:
        curr_model = {}
        for key, val in model_dict[model].items():
            if not(isinstance(val, float) and math.isnan(val)): 
                curr_model[key] = val
        curr_model.setdefault('metadata', {})['model'] = model
        
        curr_module, curr_class = curr_model['module'], curr_model['class']
        curr_instance = getattr(importlib.import_module(curr_module), curr_class)(**curr_model)
        population_list.append(curr_instance)

    return population_list
