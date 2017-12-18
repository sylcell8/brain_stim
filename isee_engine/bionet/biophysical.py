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

    axon_diams = [hobj.axon[0].diam, hobj.axon[0].diam]
    for sec in hobj.all:
        section_name = sec.name().split(".")[1][:4]
        if section_name == 'axon':
            axon_diams[1] = sec.diam

    for sec in hobj.axon:
        h.delete_section(sec=sec)

    h.execute('create axon[2]', hobj)
    for index, sec in enumerate(hobj.axon):
        sec.L = 30
        sec.diam = axon_diams[index]  # 1
        hobj.axonal.append(sec=sec)
        hobj.all.append(sec=sec)  # need to remove this comment

    hobj.axon[0].connect(hobj.soma[0], 1, 0)
    hobj.axon[1].connect(hobj.axon[0], 1, 0)

    h.define_shape()


def set_params(hobj, params_file_name):

    params_dict = json.load(open(params_file_name, 'r'))
    passive = params_dict['passive'][0]
    genome = params_dict['genome']
    conditions = params_dict['conditions'][0]

    section_map = {}
    for sec in hobj.all:
        section_name = sec.name().split(".")[1][:4]
        if section_name in section_map:
            section_map[section_name].append(sec)
        else:
            section_map[section_name] = [sec]

    for sec in hobj.all:
        sec.insert('pas')
        sec.insert('extracellular')

    if 'e_pas' in passive:
        e_pas_val = passive['e_pas']
        for sec in hobj.all:
            for seg in sec:
                seg.pas.e = e_pas_val

    if 'ra' in passive:
        ra_val = passive['ra']
        for sec in hobj.all:
            sec.Ra = ra_val

    if 'cm' in passive:
        for cm_dict in passive['cm']:
            cm = cm_dict['cm']
            for sec in section_map.get(cm_dict['section'], []):
                sec.cm = cm

    for genome_dict in genome:
        g_section = genome_dict['section']
        if genome_dict['section'] == 'glob':
            print("WARNING: There is a section called glob, probably old json file")
            continue

        g_value = float(genome_dict['value'])
        g_name = genome_dict['name']
        g_mechanism = genome_dict.get("mechanism", "")
        for sec in section_map.get(g_section, []):
            if g_mechanism != "":
                sec.insert(g_mechanism)
            setattr(sec, g_name, g_value)

    if 'erev' in conditions:
        for erev in conditions['erev']:
            erev_section = erev['section']
            erev_ena = erev['ena']
            erev_ek = erev['ek']
            if erev_section in section_map:
                for sec in section_map.get(erev_section, []):
                    if h.ismembrane('k_ion', sec=sec) == 1:
                        setattr(sec, 'ek', erev_ek)
                    if h.ismembrane('na_ion', sec=sec) == 1:
                        setattr(sec, 'ena', erev_ena)
            else:
                print("Warning: can't set erev for {}, section array doesn't exist".format(erev_section))

    else:
        print("Warning: erev section missing")


