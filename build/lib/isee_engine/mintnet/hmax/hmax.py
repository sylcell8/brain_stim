import numpy as np
import sys
import json
from S1_Layer import S1_Layer
from C_Layer import C_Layer
from S_Layer import S_Layer
from Sb_Layer import Sb_Layer
from ViewTunedLayer import ViewTunedLayer
from Readout_Layer import Readout_Layer
import tensorflow as tf
import os
import h5py
import pandas as pd

class hmax (object):

    def __init__(self,config_dir):  #,num_cores=8):

        self.name = config_dir

        self.config_file = os.path.join(config_dir,'config_'+config_dir+'.json')
        with open(self.config_file,'r') as f:
            self.config_data = json.loads(f.read())

        with open(self.config_data['train_state_file'],'r') as f:
            self.train_state = json.loads(f.read())

        self.output_dir = os.path.join(self.name,'output')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # self.weight_dir = os.path.join(self.name,'weights')
        # if not os.path.exists(self.weight_dir):
        #     os.makedirs(self.weight_dir)

        self.node_file = self.config_data['nodes']  #node_file
        self.model_file = self.config_data['node_types']
        #self.model_file = model_file

        self.nodes = {}

        # read model table
        model_dict = {}
        modelf = open(self.model_file,'r')
        for line in modelf:
            if line[0]=='#':  continue
            model_id, model_class = line.split()
            model_dict[model_id] = model_class
        modelf.close()

        self.train_order = []
        #self.train_state = train_state
        # construct nodes
        nodef = open(self.node_file,'r')
        for line in nodef:
            if line[0]=='#': continue
            node_name, node_type_name, input_node, json_file_name = line.split()

            json_file = open(json_file_name,'r')
            node_dict = json.loads(json_file.read())
            json_file.close()

            #print node_dict
            #print

            model_class = model_dict[node_type_name]

            print "Constructing node:  ", node_name


            if model_class=='S1_Layer':
                node_type = S1_Layer
                freq_channel_params = node_dict['freq_channel_params']
                input_shape = node_dict['input_shape']
                self.input_shape = input_shape
                orientations = node_dict['orientations']

                self.nodes[node_name] = node_type(node_name,input_shape,freq_channel_params,orientations)  #,num_cores=num_cores)
                #writer = tf.train.SummaryWriter('tmp/hmax', self.nodes['s1'].tf_sess.graph_def)
                #merged = tf.merge_all_summaries()

                #writer.add_summary(self.nodes[node_name].tf_sess.run(merged),0)

            if model_class=='C_Layer':
                node_type = C_Layer
                bands = node_dict['bands']


                self.nodes[node_name] = node_type(node_name,self.nodes[input_node],bands)
                #writer = tf.train.SummaryWriter('tmp/hmax', self.nodes['s1'].tf_sess.graph_def)

            if model_class=='S_Layer':
                node_type = S_Layer
                K = node_dict['K']
                weight_file = node_dict['weight_file']
                if weight_file=='':  weight_file=None
                pool_size = node_dict['pool_size']
                grid_size = node_dict['grid_size']

                self.train_order += [node_name]

                self.nodes[node_name] = node_type(node_name,self.nodes[input_node],grid_size,pool_size,K,file_name=weight_file)

            if model_class=='Sb_Layer':
                node_type = Sb_Layer
                K = node_dict['K']
                weight_file = node_dict['weight_file']
                if weight_file=='':  weight_file=None
                pool_size = node_dict['pool_size']
                grid_size = node_dict['grid_size']

                self.train_order += [node_name]

                self.nodes[node_name] = node_type(node_name,self.nodes[input_node],grid_size,pool_size,K,file_name=weight_file)

            if model_class=='ViewTunedLayer':
                node_type = ViewTunedLayer
                K = node_dict['K']
                input_nodes = node_dict['inputs']
                input_nodes = [self.nodes[node] for node in input_nodes]
                weight_file = node_dict['weight_file']
                if weight_file=='':  weight_file=None
                alt_image_dir = node_dict['alt_image_dir']

                self.train_order += [node_name]

                #print "alt_image_dir=",alt_image_dir
                self.nodes[node_name] = node_type(node_name,K,alt_image_dir,*input_nodes,file_name=weight_file)

            if model_class=='Readout_Layer':
                node_type = Readout_Layer
                K = node_dict['K']
                input_nodes = self.nodes[input_node]
                weight_file = node_dict['weight_file']
                if weight_file=='':  weight_file=None
                alt_image_dir = node_dict['alt_image_dir']
                lam = node_dict['lam']

                self.train_order += [node_name]

                self.nodes[node_name] = node_type(node_name,self.nodes[input_node],K,lam,alt_image_dir,file_name=weight_file)

            # print "Done"
            # print

        nodef.close()



        self.node_names = self.nodes.keys()

        self.input_shape = (self.nodes['s1'].input_shape[1], self.nodes['s1'].input_shape[2])

        print "Done"
        #writer = tf.train.SummaryWriter('tmp/hmax', self.nodes['s1'].tf_sess.graph_def)


    #def __str__(self):



    @classmethod
    def load(cls,config_dir):
        return cls(config_dir)

    def train(self):  #,alt_image_dict=None):

        # if alt_image_dict==None:
        #     alt_image_dict={}

        image_dir = self.config_data['image_dir']

        for node in self.train_order:
            if not self.train_state[node]:
                print "Training Node:  ", node

                if hasattr(self.nodes[node],'alt_image_dir') and self.nodes[node].alt_image_dir!='':
                    print "\tUsing alternate image directory:  ",  self.nodes[node].alt_image_dir  # alt_image_dict[node]
                    self.nodes[node].train(self.nodes[node].alt_image_dir,batch_size=self.config_data['batch_size'],image_shape=self.input_shape)
                    self.train_state[node]=True
                else:
                    print "\tUsing default image directory:  ", image_dir
                    self.nodes[node].train(image_dir,batch_size=self.config_data['batch_size'],image_shape=self.input_shape)
                    self.train_state[node]=True


                # if node not in alt_image_dict:
                #     print "\tUsing default image directory:  ", image_dir
                #     self.nodes[node].train(image_dir,batch_size=self.config_data['batch_size'],image_shape=self.input_shape)
                #     self.train_state[node]=True
                # else:
                #     print "\tUsing alternate image directory:  ", alt_image_dict[node]
                #     self.nodes[node].train(alt_image_dict[node],batch_size=self.config_data['batch_size'],image_shape=self.input_shape)
                #     self.train_state[node]=True

                print "Done"

            with open(self.config_data['train_state_file'], 'w') as f:
                f.write(json.dumps(self.train_state))


    def run_stimulus(self,stimulus, node_table=None, output_file='output'):
        '''stimulus is an instance of one of the mintnet.Stimulus objects, i.e. LocallySparseNoise'''

        if output_file[-3:]!=".ic":
            output_file = output_file+".ic"  # add *.ic suffix if not already there

        stim_template = stimulus.get_image_input(new_size=self.input_shape, add_channels=True)

        print "Creating new output file:  ", output_file, " (and removing any previous one)"
        if os.path.exists(output_file):
            os.remove(output_file)
        output_h5 = h5py.File(output_file,'w')

        T, y, x, K = stim_template.shape
        all_nodes = self.nodes.keys()

        if node_table is None:  # just compute everything and return it all; good luck!

            new_node_table = pd.DataFrame(columns=['node','band'])

            compute_list = []
            for node in all_nodes:

                add_to_node_table, new_compute_list = self.nodes[node].get_compute_ops()
                new_node_table = new_node_table.append(add_to_node_table,ignore_index=True)
                compute_list += new_compute_list
        else:
            compute_list = []

            new_node_table = node_table.sort_values('node')
            new_node_table = new_node_table.reindex(np.arange(len(new_node_table)))

            for node in all_nodes:
                unit_table = new_node_table[node_table['node']==node]
                if (new_node_table['node']==node).any():
                    _, new_compute_list = self.nodes[node].get_compute_ops(unit_table=unit_table)

                    compute_list += new_compute_list


        # create datasets in hdf5 file from node_table, with data indexed by table index
        for i, row in new_node_table.iterrows():

            output_shape = tuple([T] + [ int(x) for x in compute_list[i].get_shape()[1:]])
            output_h5.create_dataset(str(i), output_shape, dtype=np.float32)



        batch_size = self.config_data['batch_size']
        num_batches = T/batch_size
        if T%self.config_data['batch_size']!=0:
            num_batches += 1

        for i in range(num_batches):
            sys.stdout.write( '\r{0:.02f}'.format(float(i)*100/num_batches)+'% done')
            sys.stdout.flush()
            output_list = self.nodes[all_nodes[0]].tf_sess.run(compute_list,feed_dict={self.nodes[all_nodes[0]].input: stim_template[i*batch_size:(i+1)*batch_size]})

            for io, output in enumerate(output_list):
                # dataset_string = node_table['node'].loc[io] + "/" + str(int(node_table['band'].loc[io]))
                # output_h5[dataset_string][i*batch_size:(i+1)*batch_size] = output

                output_h5[str(io)][i*batch_size:(i+1)*batch_size] = output
        sys.stdout.write( '\r{0:.02f}'.format(float(100))+'% done')
        sys.stdout.flush()

        output_h5['stim_template'] = stimulus.stim_template
        output_h5.close()
        new_node_table.to_hdf(output_file,'node_table')
        if hasattr(stimulus,'label_dataframe') and stimulus.label_dataframe is not None:
            stimulus.label_dataframe.to_hdf(output_file,'labels')
        stimulus.stim_table.to_hdf(output_file,'stim_table')


    def get_exemplar_node_table(self):

        node_table = pd.DataFrame(columns=['node','band','y','x'])
        for node in self.nodes:
            node_output = self.nodes[node].output
            if hasattr(self.nodes[node],'band_shape'):
                for band in node_output:
                    y,x = [int(x) for x in node_output[band].get_shape()[1:3]]
                    y /= 2
                    x /= 2
                    new_row = pd.DataFrame([[self.nodes[node].node_name, band, y, x]], columns=['node','band','y','x'])
                    node_table = node_table.append(new_row, ignore_index=True)
            else:
                new_row = pd.DataFrame([[self.nodes[node].node_name]], columns=['node'])
                node_table = node_table.append(new_row, ignore_index=True)

        return node_table


    def generate_output(self):

        from isee_engine.mintnet.Image_Library import Image_Library
        import matplotlib.pyplot as plt

        try:
            im_lib = Image_Library(self.config_data['image_dir'],new_size=self.input_shape)
        except OSError as e:
            print '''A repository of images (such as a collection from ImageNet - http://www.image-net.org) is required for input.
                An example would be too large to include in the isee_engine itself.
                Set the path for this image repository in hmax/config_hmax.json'''
            raise e

        image_data = im_lib(1)

        fig, ax = plt.subplots(1)
        ax.imshow(image_data[0,:,:,0],cmap='gray')

        fig.savefig(os.path.join(self.output_dir,'input_image'))
        plt.close(fig)

        nodes = self.nodes

        for node_to_plot in nodes:
            print "Generating output for node ", node_to_plot
            node_output_dir = os.path.join(self.output_dir,node_to_plot)

            if not os.path.exists(node_output_dir):
                os.makedirs(node_output_dir)

            if type(self.nodes[node_to_plot])==ViewTunedLayer:
                print "ViewTunedLayer"
                self.nodes[node_to_plot].compute_output(image_data)
                continue

            if type(self.nodes[node_to_plot])==Readout_Layer:
                print "Readout_Layer"
                self.nodes[node_to_plot].compute_output(image_data)
                continue

            num_bands = len(nodes[node_to_plot].output)

            if type(self.nodes[node_to_plot])==S1_Layer or node_to_plot=='c1':
                #print "Yes, this is an S1_Layer"
                num_filters_to_plot = 4
                fig, ax = plt.subplots(num_filters_to_plot,num_bands,figsize=(20,8))
                #fig2,ax2 = plt.subplots(num_filters_to_plot,num_bands,figsize=(20,8))
            else:
                num_filters_to_plot = 8
                fig, ax = plt.subplots(num_filters_to_plot,num_bands,figsize=(20,8))

            for band in range(num_bands):
                result = nodes[node_to_plot].compute_output(image_data,band)
                #print result[band].shape
                n, y,x,K = result.shape

                for k in range(num_filters_to_plot):

                    if num_bands!=1:
                        ax[k,band].imshow(result[0,:,:,k],interpolation='nearest',cmap='gray')
                        ax[k,band].axis('off')
                    else:
                        ax[k].imshow(result[0,:,:,k],interpolation='nearest',cmap='gray')
                        ax[k].axis('off')

                # if type(self.nodes[node_to_plot])==S1_Layer:
                #     for k in range(num_filters_to_plot):

                #         ki = 4+k
                #         ax2[k,band].imshow(result[0,:,:,ki],interpolation='nearest',cmap='gray')
                #         ax2[k,band].axis('off')

            if type(self.nodes[node_to_plot])==S1_Layer:
                fig.savefig(os.path.join(node_output_dir,'output_phase0.pdf'))
                #fig2.savefig(os.path.join(node_output_dir,'output_phase1.pdf'))
                #plt.close(fig2)
            else:
                fig.savefig(os.path.join(node_output_dir,'output.pdf'))

            plt.close(fig)
