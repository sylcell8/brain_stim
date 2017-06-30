from neuron import h
import json

    
def set_morphology(hobj, morph_file):
    '''
    Set morphology for the cell from a swc
    
    Parameters
    ---------- 
    hobj: instance of a Biophysical template
        NEURON's cell object
    morph_file: string 
        name of swc file containing 3d coordinates of morphology
    '''

    swc = h.Import3d_SWC_read()
    swc.quiet = True
    swc.input(str(morph_file))
    imprt = h.Import3d_GUI(swc, 0)
    imprt.quiet = True
    imprt.instantiate(hobj)


def set_segs(hobj):    
    '''
    Define number of segments in a cell
    
    Parameters
    ----------
    hobj: instance of a Biophysical template
        NEURON's cell object
    '''

    for sec in hobj.all:
        sec.nseg = 1 + 2 * int(sec.L / 40)


def fix_axon(hobj):  
    '''
    Replace reconstructed axon with a stub
    
    Parameters
    ----------
    hobj: instance of a Biophysical template
        NEURON's cell object
    '''

    
    for sec in hobj.axon:
        h.delete_section(sec=sec)
      
    h.execute('create axon[2]', hobj)

        
    for sec in hobj.axon:
        sec.L = 30
        sec.diam = 1
        hobj.axonal.append(sec=sec)
        hobj.all.append(sec=sec)    # need to remove this comment

    hobj.axon[0].connect(hobj.soma[0], 0.5, 0)
    hobj.axon[1].connect(hobj.axon[0], 1, 0)


    h.define_shape()



def fix_axon_all_active(hobj):  
    '''
        need temporary because axon is treated differently
    '''
    pass
    

def set_params_perisomatic(hobj, params_file_name):

    '''
    Set biophysical parameters for the cell
    
    Parameters
    ---------- 
    hobj: instance of a Biophysical template
        NEURON's cell object
    params_file_name: string 
        name of json file containing biophysical parameters for cell's model which determine spiking behavior
    '''

    with open(params_file_name) as biophys_params_file:
        biophys_params = json.load(biophys_params_file)

    passive = biophys_params['passive'][0]
    conditions = biophys_params['conditions'][0]
    genome = biophys_params['genome']

    # Set passive properties
    cm_dict = dict([(c['section'], c['cm']) for c in passive['cm']])
    for sec in hobj.all:
        sec.Ra = passive['ra']
        sec.cm = cm_dict[sec.name().split(".")[1][:4]]
        sec.insert('pas')
        sec.insert('extracellular')

        for seg in sec:
            seg.pas.e = passive["e_pas"]

    # Insert channels and set parameters
    for p in genome:
        sections = [s for s in hobj.all if s.name().split(".")[1][:4] == p["section"]]
        for sec in sections:
            if p["mechanism"] != "":
                sec.insert(p["mechanism"])
            setattr(sec, p["name"], p["value"])
    #
    # Set reversal potentials
    for erev in conditions['erev']:
        sections = [s for s in hobj.all if s.name().split(".")[1][:4] == erev["section"]]
        for sec in sections:
            sec.ena = erev["ena"]
            sec.ek = erev["ek"]

######################################################################################################################

def set_params_all_active(hobj, params_file_name):

    '''Configure a neuron after the cell morphology has been loaded.'''

    with open(params_file_name) as biophys_params_file:    
        biophys_params = json.load(biophys_params_file)

    passive = biophys_params['passive'][0]
    genome = biophys_params['genome']
    conditions = biophys_params['conditions'][0]

    if "ra" in passive:
        for sec in hobj.all:
            sec.Ra = passive['ra']

    if "cm" in passive:
        cm_dict = dict([(c['section'], c['cm']) for c in passive['cm']])
        for sec in hobj.all:
            sec.cm = cm_dict[sec.name().split(".")[1][:4]]

    #IMPORTANT !!!!!!
    for sec in hobj.all:
        for seg in sec:
            sec.insert('pas')
            sec.insert('extracellular')

    if "e_pas" in passive:
        for sec in hobj.all:
            for seg in sec:
                seg.pas.e = passive['e_pas']

    for p in genome:
        sections = [s for s in hobj.all if s.name().split(".")[1][:4] == p["section"]]
        if p["section"] == "glob": print "WARNING: There is a section called glob, probably old json file"

        for sec in sections:
            # print sec.name()
            if p["mechanism"] != "":
                sec.insert(p["mechanism"])
            setattr(sec, p["name"], float(p["value"]))


    # Set reversal potentials
    for erev in conditions['erev']:
        erev_section_array = erev["section"]
        ek = float(erev["ek"])
        ena = float(erev["ena"])

        # print 'Setting ek to %.6g and ena to %.6g in %s' % (ek, ena, erev_section_array)
        if hasattr(hobj, erev_section_array):
            for section in getattr(hobj, erev_section_array):
                if h.ismembrane("k_ion", sec=section) == 1: setattr(section, 'ek', ek)
                if h.ismembrane("na_ion", sec=section) == 1: setattr(section, 'ena', ena)
        else:
            print "Warning: can't set erev for %s, section array doesn't exist" % erev_section_array


    # for sec in hobj.all:
    #     print sec.name().split(".")[1][:4], "Ra:", sec.Ra, "cm:", sec.cm, "e_pas:", sec.e_pas, "g_pas:", sec.g_pas
    #     if h.ismembrane("CaDynamics", sec=sec): print sec.name().split(".")[1][:4], sec.gamma_CaDynamics

    # # Insert channels and set parameters
    # for p in genome:
    #     section_array = p["section"]
    #     mechanism = p["mechanism"]
    #     param_name = p["name"]
    #     param_value = float(p["value"])
    #     # print section_array, mechanism, param_name, param_value
    #
    #
    #     if section_array == "glob":    h(p["name"] + " = %g " % p["value"])
    #     # print section_array
    #     if hasattr(hobj, section_array):
    #         print getattr(hobj, section_array)
    #             if mechanism != "":
    #                 print 'Adding mechanism %s to %s' % (mechanism, section_array)
    #                 for section in getattr(hobj, section_array):
    #                     if h.ismembrane(str(mechanism), sec=section) != 1:  section.insert(mechanism)
    #
    #             print 'Setting %s to %.6g in %s' % (param_name, param_value, section_array)
    #             for section in getattr(hobj, section_array):  setattr(section, param_name, param_value)




