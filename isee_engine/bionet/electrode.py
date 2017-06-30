import numpy as np
import math
import pandas as pd



class Electrode():
    '''
    Extracellular electrode 
    '''


    def __init__(self,conf):
        '''
        Create an array
        '''
        self.conf = conf
        electrode_file = self.conf["extracellular_electrode"]["positions"]       

        el_df = pd.read_csv(electrode_file,sep=' ')

        self.pos = el_df.as_matrix(columns=['x_pos','y_pos','z_pos']).T      # convert coordinates to ndarray, The first index is xyz and the second is the channel number  

        self.nsites = self.pos.shape[1]
        
        self.conf['run']['nsites'] = self.nsites  # add to the config

        self.map = {}   # mapping segment coordinates

        
    def drift(self):    # will incude function to model electrode drift
        
        pass
    
    def clear_ecp_combined(self):

        self.ecp_combined = np.zeros(self.nsites) # array to add cells.ecp on each rank


    def get_ecp(self,gid,im):

        cell_map = self.map[gid]

        return np.dot(cell_map,im)    

    def add_to_ecp_combined(self,ecp):
        
        self.ecp_combined += ecp  # accumulate contributions 


    def map_segs(self,gid,seg_coords):

        '''
        Precompute mapping from segment to electrode locations 
        '''        
        sigma = 0.3 # mS/mm

        r05 = (seg_coords['p0'] + seg_coords['p1'])/2
        dl = seg_coords['p1'] - seg_coords['p0']
        
        nseg = r05.shape[1]
        
        cell_map = np.zeros((self.nsites,nseg))


        for j in xrange(self.nsites):   # calculate mapping for each site on the electrode
            
            rel=np.expand_dims(self.pos[:,j],axis=1)   # coordinates of a j-th site on the electrode
           
            rel_05 = rel - r05 # distance between electrode and segment centers 

            r2 = np.einsum('ij,ij->j',rel_05,rel_05)    # compute dot product column-wise, the resulting array has as many columns as original
            
            rlldl = np.einsum('ij,ij->j',rel_05,dl)    # compute dot product column-wise, the resulting array has as many columns as original
            dlmag = np.linalg.norm(dl, axis=0) # length of each segment
#                print 'dlmag:',dlmag.shape
            rll = abs(rlldl/dlmag)   # component of r parallel to the segment axis it must be always positive
            
            rT2 = r2 -rll**2  # squre of perpendicular component   
                
            up = rll + dlmag/2; 
            low = rll - dlmag/2; 
            num = up + np.sqrt(up**2 + rT2)
            den = low + np.sqrt(low**2 + rT2)

            cell_map[j,:] = np.log(num/den)/dlmag # units of (um)    use with im_ (total seg current)

        cell_map*=1/(4*math.pi*sigma) 

        self.map[gid] = cell_map
        