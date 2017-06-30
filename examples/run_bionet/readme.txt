cd to run directory:

/data/mat/slg/ice/sims/layer4/ll2

/net - internal nodes and edges
/output*
config.json - contains paths to files and configuration parameters

"overwrite_output_dir": true  -  will overwrite the output directory

mpirun -np 4 nrniv -mpi -python run_sim.py config.json


check runlog.txt for status - even possible during simuation run. These are outputs from io.print2log0()
./ouptut* dir includes a copy of config.json

/state - dir to save entire internal state using NEURON's save state capability

link to isee_engine
http://stash.corp.alleninstitute.org/projects/INF/repos/isee_engine/browse


to clone: 
git clone url


to run on a cluster:

set the queue to either "mindscope" for production run or "mindscope-dbg" for debugging in qsub_job.tmpl

ssh qmaster

cd to run directory



qsub_run.sh 4 24 joll2 /data/mat/slg/ice/sims/layer4/ll2 config.json


qstat -u sergeyg  check on your jobs
qstat -n mindscope

ctrl+r to get access to history
