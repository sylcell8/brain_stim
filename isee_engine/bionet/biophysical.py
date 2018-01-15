from neuron import h
import json
import numpy as np
from sklearn.decomposition import PCA
from isee_engine.bionet.morphology import Morphology
from decimal import *



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


def get_axon_direction(hobj):

    for sec in hobj.somatic:
        n3d = int(h.n3d())  # get number of n3d points in each section
        soma_end = np.asarray([h.x3d(n3d - 1), h.y3d(n3d - 1), h.z3d(n3d - 1)])
        mid_point = int(n3d / 2)
        soma_mid = np.asarray([h.x3d(mid_point), h.y3d(mid_point), h.z3d(mid_point)])

    for sec in hobj.all:
        section_name = sec.name().split(".")[1][:4]
        if section_name == 'axon':
            n3d = int(h.n3d())  # get number of n3d points in each section
            axon_p3d = np.zeros((n3d, 3))  # to hold locations of 3D morphology for the current section
            for i in range(n3d):
                axon_p3d[i, 0] = h.x3d(i)
                axon_p3d[i, 1] = h.y3d(i)  # shift coordinates such to place soma at the origin.
                axon_p3d[i, 2] = h.z3d(i)

    #Add soma coordinates to the list
    p3d = np.concatenate(([soma_mid] , axon_p3d), axis=0)

    #Compute PCA
    pca = PCA(n_components=3)
    pca.fit(p3d)
    unit_v = pca.components_[0]

    mag_v = np.sqrt(pow(unit_v[0],2)+pow(unit_v[1],2)+pow(unit_v[2],2))
    unit_v[0] = unit_v[0] / mag_v
    unit_v[1] = unit_v[1] / mag_v
    unit_v[2] = unit_v[2] / mag_v

    #Find the direction
    axon_end = axon_p3d[-1]
    if (np.dot(unit_v, axon_end) < 0) :
        unit_v = unit_v * -1

    axon_seg_coor = np.zeros((4,3))
    # unit_v = np.asarray([0,1,0])
    axon_seg_coor[0] =  soma_end
    axon_seg_coor[1] =  soma_end + (unit_v * 30.)
    axon_seg_coor[2] =  soma_end + (unit_v * 30.)
    axon_seg_coor[3] =  soma_end + (unit_v * 60.)

    return axon_seg_coor



def fix_axon_perisomatic(hobj):
    print "fix_axon_perisomatic"

    all_sec_names = []
    for sec in hobj.all:
        all_sec_names.append(sec.name().split(".")[1][:4])

    if 'axon' not in all_sec_names:
        print "ERROR: There is no axonal recostruction in swc file"
        print "You can continute by choosing fix_axon_all_active_OLD"
        exit()
    else:
        beg1, end1, beg2, end2 = get_axon_direction(hobj)

    for sec in hobj.axon:
        h.delete_section(sec=sec)
    h.execute('create axon[2]', hobj)

    h.pt3dadd(beg1[0], beg1[1], beg1[2], 1, sec=hobj.axon[0])
    h.pt3dadd(end1[0], end1[1], end1[2], 1, sec=hobj.axon[0])
    hobj.all.append(sec=hobj.axon[0])
    h.pt3dadd(beg2[0], beg2[1], beg2[2], 1, sec=hobj.axon[1])
    h.pt3dadd(end2[0], end2[1], end2[2], 1, sec=hobj.axon[1])
    hobj.all.append(sec=hobj.axon[1])

    hobj.axon[0].connect(hobj.soma[0], 0.5, 0)
    hobj.axon[1].connect(hobj.axon[0], 1.0, 0)

    hobj.axon[0].L = 30.0
    hobj.axon[1].L = 30.0

    h.define_shape()

    for sec in hobj.axon:
        # print "sec.L:", sec.L
        if (np.abs(30-sec.L) > 0.0001):
            print "ERROR: axon stub L is less than 30"
            exit()

    # for sec in hobj.allsec():
    #     n = int(h.n3d())
    # #     print sec.name(), n, sec.L
    #     for i in range(n):
    #         print  i, h.x3d(i), h.y3d(i), h.z3d(i)

def fix_axon_all_active(hobj):
    print "fix_axon_all_active"
    all_sec_names = []
    for sec in hobj.all:
        all_sec_names.append(sec.name().split(".")[1][:4])

    if 'axon' not in all_sec_names:
        print "ERROR: There is no axonal recostruction in swc file"
        print "You can continute by choosing fix_axon_all_active_OLD"
        exit()
    else:
        beg1, end1, beg2, end2 = get_axon_direction(hobj)

    axon_diams = [hobj.axon[0].diam, hobj.axon[0].diam]
    for sec in hobj.all:
        section_name = sec.name().split(".")[1][:4]
        if section_name == 'axon':
            axon_diams[1] = sec.diam

    for sec in hobj.axon:
        h.delete_section(sec=sec)
    h.execute('create axon[2]', hobj)
    hobj.axon[0].connect(hobj.soma[0], 1.0, 0)
    hobj.axon[1].connect(hobj.axon[0], 1.0, 0)

    h.pt3dadd(beg1[0], beg1[1], beg1[2], axon_diams[0], sec=hobj.axon[0])
    h.pt3dadd(end1[0], end1[1], end1[2], axon_diams[0], sec=hobj.axon[0])
    hobj.all.append(sec=hobj.axon[0])
    h.pt3dadd(beg2[0], beg2[1], beg2[2], axon_diams[1], sec=hobj.axon[1])
    h.pt3dadd(end2[0], end2[1], end2[2], axon_diams[1], sec=hobj.axon[1])
    hobj.all.append(sec=hobj.axon[1])

    hobj.axon[0].L = 30.0
    hobj.axon[1].L = 30.0

    h.define_shape()

    for sec in hobj.axon:
        print "sec.L:", sec.L
        if (np.abs(30 - sec.L) > 0.0001):
            print "ERROR: axon stub L is less than 30"
            exit()

    # for sec in hobj.allsec():
    #     n = int(h.n3d())
    # #     print sec.name(), n, sec.L
    #     for i in range(n):
    #         print  i, h.x3d(i), h.y3d(i), h.z3d(i)

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




# def fix_axon_all_active_OLD(hobj):
#         print "OLDDDDDD"
#         axon_diams = [hobj.axon[0].diam, hobj.axon[0].diam]
#         for sec in hobj.all:
#             section_name = sec.name().split(".")[1][:4]
#             if section_name == 'axon':
#                 axon_diams[1] = sec.diam
#
#         for sec in hobj.axon:
#             h.delete_section(sec=sec)
#
#         h.execute('create axon[2]', hobj)
#         for index, sec in enumerate(hobj.axon):
#             sec.L = 30
#             sec.diam = axon_diams[index]  # 1
#             hobj.axonal.append(sec=sec)
#             hobj.all.append(sec=sec)  # need to remove this comment
#
#         hobj.axon[0].connect(hobj.soma[0], 1.0, 0)
#         hobj.axon[1].connect(hobj.axon[0], 1.0, 0)
#
#         h.define_shape()
# #
# # #
# def fix_axon_perisomatic_OLD(hobj):
#         print "fix_axon_perisomatic_OLD"
#
#         for sec in hobj.axon:
#             h.delete_section(sec=sec)
#         h.execute('create axon[2]', hobj)
#
#         for sec in hobj.axon:
#             sec.L = 30
#             sec.diam = 1
#             hobj.axonal.append(sec=sec)
#             hobj.all.append(sec=sec)  # need to remove this comment
#
#         hobj.axon[0].connect(hobj.soma[0], 0.5, 0)
#         hobj.axon[1].connect(hobj.axon[0], 1.0, 0)
#
#         h.define_shape()


# def get_axon_direction2(hobj):
#
#     p3dsoma = get_soma_pos(hobj)
#     psoma = p3dsoma
#
#     for sec in hobj.all:
#         section_name = sec.name().split(".")[1][:4]
#         if section_name == 'axon':
#             n3d = int(h.n3d())  # get number of n3d points in each section
#             p3d = np.zeros((n3d + 1, 3))  # to hold locations of 3D morphology for the current section
#             for i in range(n3d):
#                 p3d[i, 0] = h.x3d(i)
#                 p3d[i, 1] = h.y3d(i)   # shift coordinates such to place soma at the origin.
#                 p3d[i, 2] = h.z3d(i)
#                 # print h.x3d(i), h.y3d(i), h.z3d(i)
#             p3d[n3d] = psoma
#
#
#     x = np.mean(p3d[:,0])
#     y = np.mean(p3d[:,1])
#     z = np.mean(p3d[:,2])
#     rmean = [x, y, z]
#     # print rmean
#     v = rmean - psoma
#     magnitude = np.sqrt(pow(v[0], 2) + pow(v[1], 2) + pow(v[2], 2))
#
#     unit_v = np.zeros((1, 3))
#     unit_v[0][0] = v[0]/magnitude
#     unit_v[0][1] = v[1]/magnitude
#     unit_v[0][2] = v[2]/magnitude
#
#     # print [x * 30 for x in unit_v] + p3d[0]
#
#     axon_seg_coor = np.zeros((4,3))
#     axon_seg_coor[0] = p3d[0]
#     axon_seg_coor[1] = p3d[0] + [x * 30 for x in unit_v]
#     axon_seg_coor[2] = p3d[0] + [x * 30 for x in unit_v]
#     axon_seg_coor[3] = p3d[0] + [x * 60 for x in unit_v]
#
#     temp1 = axon_seg_coor[1] - axon_seg_coor[0]
#     temp2 = axon_seg_coor[3] - axon_seg_coor[2]
#     # print '{0:.30}'.format(np.sqrt(pow(temp1[0], 2) + pow(temp1[1], 2) + pow(temp1[2], 2)))
#     # print '{0:.30}'.format(np.sqrt(pow(temp2[0], 2) + pow(temp2[1], 2) + pow(temp2[2], 2)))
#     # print p3d
#     # print axon_seg_coor[0]
#     # print axon_seg_coor[1]
#     # print axon_seg_coor[2]
#     # print axon_seg_coor[3]
#
#     return axon_seg_coor


# def print_shape(hobj):
#     for sec in hobj.allsec():
#         if 'apic' in sec.name() or 'dend' in sec.name():
#             continue
#
#         n3d = int(h.n3d())
#         for i in range(n3d):
#             print sec.name(), ':', h.x3d(i), h.y3d(i), h.z3d(i)
#
#     print h.toplogy()
