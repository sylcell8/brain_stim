export ALLENSDK=/shared/bioapps/infoapps/lims2_modules/lib/allensdk
export NRN_HOME=/shared/utils.x86_64/nrn-7.4-1370
export NRN_BIN=${NRN_HOME}/x86_64/bin

export PYTHON_BIN=/shared/utils.x86_64/python-2.7/bin
export HYDRA_BIN=/shared/utils.x86_64/hydra-3.0.4/bin
export OPENMPI_BIN=/usr/lib64/openmpi/bin

export LOCAL_BIN=/home/tomcat/.local/bin

export NEST_HOME=/shared/utils.x86_64/nest-2.6.0-nompi
export NEST_LIB=${NEST_HOME}/lib/python2.7/site-packages

export PATH=${HYDRA_BIN}:${PYTHON_BIN}:${LOCAL_BIN}:${NRN_BIN}:${OPENMPI_BIN}:/bin:/usr/bin

echo "PATH" $PATH

export LOCAL_LIB=/home/tomcat/.local/lib
export WORKSPACE=${bamboo.build.working.directory}
export USERLIBS=/home/tomcat/.local/lib/python2.7/site-packages
#export DISPLAY=:1.0
export PYTHONPATH=$WORKSPACE:${NRN_HOME}/lib/python:${NEST_LIB}:${USERLIBS}:${ALLENSDK}

cd examples/run_bionet
$NRN_BIN/nrnivmodl modfiles
cd ../..

export NOSE=/shared/utils.x86_64/python-2.7/bin/nosetests
$NOSE --verbosity=3 --with-xunit -x isee_engine/test