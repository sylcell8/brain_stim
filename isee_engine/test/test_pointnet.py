import nest
import numpy
import sys
import os 
default=os.getcwd()
sys.path.append('/home/jungl/isee_engine/examples/run_pointnet')
os.chdir('/home/jungl/isee_engine/examples/run_pointnet')
import configure
configure=configure.configdata()
os.chdir(default)
sys.path.append('/home/jungl/isee_engine/isee_engine/pointnet') 
import load_csv
nodes=configure.input_dir+'/'+configure.node_data
models=configure.input_dir+'/'+configure.model_data
node_info,model_info,dict_coordinates=load_csv.load_params(nodes,models) 

def check_neuron_models(name):
	models_installed=nest.Models()
	models=list(models_installed)
	if name in models:
		pass
	else:
		raise ValueError('the selected neuron model <{0}> is not installed in your NEST distribution'.format(name))



for xin in xrange(len(node_info)):
	check_neuron_models(node_info[xin,1])

