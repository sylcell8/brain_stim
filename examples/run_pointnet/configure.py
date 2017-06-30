import os
import json

class configdata:
	'''
	load necessary information for simulation

	'''
	
	fp=open('config.json','r')
	info=json.load(fp)
	sim_duration=info['run']['duration']
	sim_dt=info['run']['dt']
	overwrite_flag=info['run']['overwrite_output_dir']
	base_dir=info['manifest']['base_directory']
	input_dir=base_dir+'/'+info['manifest']['input']
	output_dir=base_dir+'/'+info['manifest']['output']
	model_dir=base_dir+'/'+info['manifest']['models']		
	if not os.path.exists(input_dir):
		raise EOFError('Input directory does not exist. Check your config files')
	if not os.path.exists(model_dir):
		raise EOFError('Model directory does not exist. Check your config files')
	if not os.path.exists(model_dir):
		os.makedirs(output_dir)
	print 'output directory was created as ',output_dir

	block=info['block']
	blocksize=info['blocksize']
	node_data=info['node_data']
	model_data=info['model_data']
	conn_data=info['conn_data']

# end of script




