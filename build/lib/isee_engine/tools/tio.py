import h5py

def load_ij_connections(file_name):

    '''
    load ij connections

    Parameters
    ----------
    file_name: string
        full path to h5 file
    
    
    Returns
    -------
    connections: h5 dataset
        includes 3 columns: indptr, src_gids, nsyns 
        indptr - index pointer to src_gids and nsyns
        the tar_gid is the index of indptr

        Usage:
        src_gids = connections['src_gids'][indptr[tar_gid]:indptr[tar_gid+1]]
        nsyns = connections['nsyns'][indptr[tar_gid]:indptr[tar_gid+1]] 

    '''    


    connections = h5py.File(file_name,'r')
    
    return connections

    