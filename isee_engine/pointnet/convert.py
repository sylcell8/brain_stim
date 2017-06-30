import sys
sys.path.append('/home/jungl/isee_engine/isee_engine') 
import nwb
from collections import defaultdict
import h5py
import numpy 

def gen_recurrent_csv(num,offset):
	conn_data=numpy.loadtxt('/home/jungl/isee_engine/isee_engine/pointnet/example_connections.dat')
	target_ids=conn_data[:,0]
	source_ids=conn_data[:,1]
	weight_scale=conn_data[:,2]

	pre=[]
	cell_num=num
	params=[]
	for xin in xrange(cell_num):
		pre.append(xin+offset)
		ind=numpy.where(source_ids==xin)

		temp_param={}
		targets=target_ids[ind]+offset
		weights=weight_scale[ind]
		delays=numpy.ones(len(ind[0]))*1.5
		targets.astype(float)
		weights.astype(float)
		temp_param['target']=targets
		temp_param['weight']=weights*1
		temp_param['delay']=delays
		params.append(temp_param)
		
	return pre, params

def gen_recurrent_h5(num,offset):
	fc=h5py.File('/data/mat/iSee_temp_shared/con_rec/con_rec120.h5')
	indptr=fc['indptr']
	cell_size=len(indptr)-1
	src_gids=fc['src_gids']
	nsyns=fc['nsyns']
	source_ids=[]
	weight_scale=[]
	target_ids=[]
	delay_v=1.5 # arbitrary value
	for xin in xrange(cell_size):
		target_ids.append(xin)
		source_ids.append(list(src_gids[indptr[xin]:indptr[xin+1]]))
		weight_scale.append(list(nsyns[indptr[xin]:indptr[xin+1]]))
	targets=defaultdict(list)
	weights=defaultdict(list)
	delays=defaultdict(list)
	for xi,xin in enumerate(target_ids):
		for yi, yin in enumerate(source_ids[xi]):
		 	targets[yin].append(xin)
			weights[yin].append(weight_scale[xi][yi])
			delays[yin].append(delay_v)
	presynaptic=[]	
	params=[]
	for xin in targets:
		presynaptic.append(xin+offset)
		temp_param={}
		temp_array=numpy.array(targets[xin])*1.0+offset
		temp_array.astype(float)
		temp_param['target']=temp_array
		temp_array=numpy.array(weights[xin])
		temp_array.astype(float)
		temp_param['weight']=temp_array
		temp_array=numpy.array(delays[xin])
		temp_array.astype(float)
		temp_param['delay']=temp_array
		params.append(temp_param)	
		
	
	return presynaptic, params
	
	


