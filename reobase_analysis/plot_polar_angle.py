import matplotlib.pyplot as plt
import reobase_utils as r
import analysis as ra
import numpy as np
import pandas as pd
from reobase_analysis.reobase_utils import StimType

SAVE = False


def plot_modulation_comparison(gid_list1, gid_list2, colname, amp, stim_type, model_type, trial, nbins, distance=None):
    if distance is not None:
        # print "I am here"
        rads, med1 = get_median(gid_list1, colname, amp, stim_type, model_type, trial, distance=distance)
        rads, med2 = get_median(gid_list2, colname, amp, stim_type, model_type, trial, distance=distance)
    else:
        rads, med1 = get_median(gid_list1, colname, amp, stim_type, model_type, trial)
        rads, med2 = get_median(gid_list2, colname, amp, stim_type, model_type, trial)
    box_data1 = [[med1[gid][i] for gid in gid_list1] for i in range(nbins - 1)]
    box_data2 = [[med2[gid][i] for gid in gid_list2] for i in range(nbins - 1)]

    filtered_data1 = []
    filtered_data2 = []

    for list in box_data1:
        filtered_data1.append([x for x in list if ~np.isnan(x)])

    for list in box_data2:
        filtered_data2.append([x for x in list if ~np.isnan(x)])

    fig, ax = plt.subplots()
    fig.set_figheight(7)
    fig.set_figwidth(15)
    boxprops = dict(linewidth=1.5)
    medianprops1 = dict(linestyle='-', linewidth=1.5, color='red')
    bp = ax.boxplot(filtered_data1, showmeans=True, boxprops=boxprops, medianprops=medianprops1, patch_artist=True)
    ax.set_xticklabels(["{0:4.2f}".format(x) for x in (np.array(rads) * 180 / np.pi)], rotation='vertical')
    ax.set_xlabel('$\Theta$ (degree)', fontsize=20)
    ax.set_title("Pyramidal cells", fontsize=20)
    ax.tick_params(labelsize=15)
    if colname == "delta_vm":
        ax.set_ylabel('$\Delta$Vm (mV)', fontsize=20)
    else:
        ax.set_ylabel('Spike frequency (Hz)', fontsize=20)

    ax.legend()

    for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']:
        plt.setp(bp[element], color='red')

    for patch in bp['boxes']:
        patch.set(facecolor='orange')

    plt.show()

    fig, ax = plt.subplots()
    fig.set_figheight(7)
    fig.set_figwidth(15)
    boxprops = dict(linewidth=1.5)
    medianprops2 = dict(linestyle='-', linewidth=1.5, color = 'blue')
    bp = ax.boxplot(filtered_data2, showmeans=True, boxprops=boxprops, medianprops=medianprops2, patch_artist=True)
    ax.set_xticklabels(["{0:4.2f}".format(x) for x in (np.array(rads) * 180 / np.pi)], rotation='vertical')
    ax.set_xlabel('$\Theta$ (degree)', fontsize=20)
    ax.set_title("Basket cells", fontsize=20)
    ax.tick_params(labelsize=15)
    if colname == "delta_vm":
        ax.set_ylabel('$\Delta$Vm (mV)', fontsize=20)
    else:
        ax.set_ylabel('Spike frequency (Hz)', fontsize=20)

    ax.legend()

    for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']:
        plt.setp(bp[element], color='blue')

    for patch in bp['boxes']:
        patch.set(facecolor='cyan')

    plt.show()

    fig, ax = plt.subplots()
    fig.set_figheight(7)
    fig.set_figwidth(15)
    boxprops = dict(linewidth=1.5)
    medianprops1 = dict(linestyle='-', linewidth=1.5, color='red')
    medianprops2 = dict(linestyle='-', linewidth=1.5, color='blue')
    bp = ax.boxplot(filtered_data1, showmeans=True, boxprops=boxprops, medianprops=medianprops1, patch_artist=True)
    for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']:
        plt.setp(bp[element], color='red')

    for patch in bp['boxes']:
        patch.set(facecolor='orange')

    bp = ax.boxplot(filtered_data2, showmeans=True, boxprops=boxprops, medianprops=medianprops2, patch_artist=True)
    for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']:
        plt.setp(bp[element], color='blue')

    for patch in bp['boxes']:
        patch.set(facecolor='cyan')

    ax.set_xticklabels(["{0:4.2f}".format(x) for x in (np.array(rads) * 180 / np.pi)], rotation='vertical')
    ax.set_xlabel('$\Theta$ (degree)', fontsize=20)
    ax.set_title("Pyramidal and Basket cells", fontsize=20)
    ax.tick_params(labelsize=15)
    if colname == "delta_vm":
        ax.set_ylabel('$\Delta$Vm (mV)', fontsize=20)
    else:
        ax.set_ylabel('Spike frequency (Hz)', fontsize=20)

    ax.legend()
    plt.show()




def get_median (gids_list, colname, amp, stim_type, model_type, trial, nbins=14, distance=None):

    rads = []
    med_dic = {}

    for gid in gids_list:
        t = generate_theta(gid, [amp], stim_type, model_type, trial)
        bins = np.linspace(0, np.pi, nbins)
        categories = pd.cut(t["theta"], bins)
        groups = t.groupby(categories)

        med = []
        for interval, g in groups:
            rads = rads + [interval.mid]
            if distance is not None:
                med.append(g[g["distance"] == distance][colname].agg(np.median, axis=0))
            else:
                med.append(g[colname].agg(np.median, axis=0))

        med_dic[gid] = med
    return rads, med_dic


def plot_median_colname_vs_theta(gids_list, colname, amp, stim_type, model_type, trial, nbins=14, distance=None):

    data_dic = {}
    rads = []
    med_dic = {}

    for gid in gids_list:
        t = generate_theta(gid, [amp], stim_type, model_type, trial)
        bins = np.linspace(0, np.pi, 14)
        categories = pd.cut(t["theta"], bins)
        groups = t.groupby(categories)

        med = []
        data = []
        for interval, g in groups:
            rads = rads + [interval.mid]
            if distance is not None:
                med.append(g[g["distance"] == distance][colname].agg(np.median, axis=0))
                data.append(g[g["distance"] == distance][colname])
            else:
                med.append(g[colname].agg(np.median, axis=0))
                data.append(g[colname])

        data_dic[gid] = data
        med_dic[gid] = med

    box_data = [[med_dic[gid][i] for gid in gids_list] for i in range(nbins - 1)]

    filtered_data = []

    for list in box_data:
        filtered_data.append([x for x in list if ~np.isnan(x)])

    fig = plt.figure()
    fig.set_figheight(7)
    fig.set_figwidth(15)
    ax = fig.add_subplot(111)

    if colname == "delta_vm":
        ax.set_title('$\Delta$Vm distribution by polar angle $\Theta$ (amp = {}, distance={})'.format(amp, distance),
                     fontsize=15)
        ax.set_ylabel('$\Delta$Vm (mV)', fontsize=20)
    else:
        ax.set_title(
            'Spike frequency distribution by polar angle $\Theta$ (amp = {}, distance={})'.format(amp, distance),
            fontsize=15)
        ax.set_ylabel('Spike frequency (Hz)', fontsize=20)

    ax.set_xlabel('$\Theta$ (degree)')
    boxprops = dict(linewidth=1.5)
    medianprops = dict(linestyle='-', linewidth=1.5, color='firebrick')
    ax.set_xlabel('$\Theta$ (degree)', fontsize=20)
    ax.tick_params(labelsize=15)
    ax.boxplot(filtered_data, showmeans=True, boxprops=boxprops, medianprops=medianprops)
    ax.set_xticklabels(["{0:4.2f}".format(x) for x in (np.array(rads) * 180 / np.pi)], rotation='vertical')
    plt.show()



def plot(t, amp, col_name, nbins=14, save_name=None):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('"{}" distribution by polar angle $\Theta$ (amp = {})'.format(col_name, amp))
    ax.set_xlabel('$\Theta$ (degree)')
    ax.set_ylabel(col_name)
    #    tc.set_theta_ticks(ax)

    n, bins = np.histogram(t.theta, bins=nbins)
#    width = bins[1] - bins[0]
    categories = pd.cut(t['theta'], bins)
    groups = t.groupby(categories)

    data = []
    rads = []

    for interval, g in groups:
        rads = rads + [interval.mid]
        data.append(g[col_name])

    boxprops = dict(linewidth=1.5)
    medianprops = dict(linestyle='-', linewidth=1.5, color='firebrick')

    ax.boxplot(data, showmeans=True, boxprops=boxprops, medianprops=medianprops)

    ax.set_xticklabels(["{0:4.2f}".format(x) for x in (np.array(rads) * 180/ np.pi)],rotation='vertical')

    ax.set_xlabel('$\Theta$ (degree)', fontsize = 12)
    ax.set_ylabel(col_name, fontsize = 12)
    ax.tick_params(labelsize=12)
    # ax.set_xlim([0,np.pi*4])
    # ax.set_ylim([0,0.01])
    # ax.spines['left']delta.set_linewidth(2)
    # ax.spines['right'].set_linewidth(2)
    # ax.spines['top'].set_linewidth(2)
    # ax.spines['bottom'].set_linewidth(2)

    # if save_name is not None:
    #     plt.savefig(save_name)
    # else:
    #     plt.show()


def XY(cell_gid, inputs, col_name, stim_type, model_type, trial, dist, nbins=14, save_name=None):

    t = r.read_cell_tables(cell_gid, inputs, stim_type, model_type, trial)
    t['theta'], t['phi'] = ra.spherical_coords(t)

    t = t[(t.distance == dist)] # exclude closest layer
    n, bins = np.histogram(t.theta, bins=nbins)
    categories = pd.cut(t['theta'], bins)
    groups = t.groupby(categories)

    X = []
    Y = []

    for interval, g in groups:
        X = X + [interval.mid]
        Y.append(g[col_name])

    return np.array(X)/np.pi,  Y
    # return np.array(X)/np.pi


def generate_theta(cell_gid, amp, stim_type, model_type, trial, *args, **kwargs):
    """ Same as 'plot' but fetches data for you """
    t = r.read_cell_tables(cell_gid, amp, stim_type, model_type, trial)
    t['theta'], t['phi'] = ra.spherical_coords(t)
    return t
    # plot(t, amp, colname, *args, **kwargs)



def pol(cell_gid, inputs, col_name, stim_type, model_type, trial, dist):
    # cell_gid = [313862022, 314900022, 320668879][1]
    t = r.read_cell_tables(cell_gid, inputs, stim_type, model_type, trial)
    t['theta'], t['phi'] = ra.spherical_coords(t)

    # tdcp = r.read_cell_tables(cell_gid, [str(x) for x in range(20,101,20)], stim_type=StimType.DC_LGN_POISSON)
    # tdcp['theta'], tdcp['phi'] = ra.spherical_coords(tdcp)

    data = t
    data = data[(data.distance == dist)] # exclude closest layer


    for amp, g in data.groupby('amp'):
        # save_name = 'polar_angle_spikes_{}_'.format(cell_gid) + r.format_amp(amp) + '.png'
        plot(g, amp, col_name= col_name)


print 'For an example try pol(313862022, "dc", "perisomatic") function'

# default()

def fit_sin(gid, inputs, col_name, stim_type, model_type, trial, dist):
    from scipy.optimize import leastsq
    import pylab as plt

    tempX, tempY = XY(gid, inputs, col_name, stim_type, model_type, trial, dist)
    YY = []
    XX = []
    niter = 0

    for y in tempY:
        if ~np.isnan(np.mean(y)):
            YY.append(y.mean())
            XX.append(tempX[niter])
        niter += 1

    guess_meanXX = np.mean(YY)
    guess_stdXX = 3 * np.std(YY) / (2 ** 0.5)
    guess_phaseXX = 0
    XX = np.asarray(XX)

    Y = [item for sublist in tempY for item in sublist]

    niter = 0
    X = []

    for y in tempY:
        for item in y:
            X.append(tempX[niter])
        niter = niter + 1

    guess_mean = np.mean(Y)
    guess_std = 3 * np.std(Y) / (2 ** 0.5)
    guess_phase = 0
    X = np.asarray(X)

    data_first_guess = guess_std * np.sin(X + guess_phase) + guess_mean
    optimize_func = lambda x: x[0] * np.sin(X + x[1]) + x[2] - Y
    est_std, est_phase, est_mean = leastsq(optimize_func, [guess_std, guess_phase, guess_mean])[0]
    data_fit = est_std * np.sin(X + est_phase) + est_mean

    data_first_guessXX = guess_stdXX * np.sin(XX + guess_phaseXX) + guess_meanXX
    optimize_funcXX = lambda x: x[0] * np.sin(XX + x[1]) + x[2] - YY
    est_stdXX, est_phaseXX, est_meanXX = leastsq(optimize_funcXX, [guess_stdXX, guess_phaseXX,guess_meanXX])[0]
    data_fitXX = est_stdXX * np.sin(XX + est_phaseXX) + est_meanXX

    plt.plot(XX * 180, YY, 'o')
    # plt.plot(XX * 180, data_fitXX, label='after fitting')
    plt.plot(XX * 180, data_fitXX, label=model_type)

    #     plt.plot(XX, np.repeat(data_fitXX.min(), np.arange(len(XX))), label='after fitting mean values')
    plt.plot(X * 180, Y, '.')

    # plt.plot(X, data_fit, label='after fitting')
    plt.xlabel('$\Theta$ (degree)', fontsize = 15)
    plt.ylabel(col_name, fontsize = 15)
    plt.tick_params(labelsize=15)
    plt.title("HETRO")
    plt.legend()
    plt.show()
    #     return np.abs(est_stdXX), est_phaseXX * 360  / (2*np.pi) , data_fitXX.min(), np.abs(est_stdXX)/data_fitXX.min()
    # return data_fitXX.min(), data_fitXX.max(), data_fitXX.max()-data_fitXX.min(), (data_fitXX.max()-data_fitXX.min()) / np.abs(data_fitXX.min())
    # return data_fitXX.max()-data_fitXX.min(), (data_fitXX.max()-data_fitXX.min()) / np.abs(data_fitXX.min())

def get_modulation (gid, inputs, col_name, stim_type, model_type, trial, dist):
    from scipy.optimize import leastsq
    import pylab as plt

    tempX, tempY = XY(gid, inputs, col_name, stim_type, model_type, trial, dist)
    YY = []
    XX = []
    niter = 0

    for y in tempY:
        if ~np.isnan(np.mean(y)):
            YY.append(y.mean())
            XX.append(tempX[niter])
        niter += 1

    guess_meanXX = np.mean(YY)
    guess_stdXX = 3 * np.std(YY) / (2 ** 0.5)
    guess_phaseXX = 0
    XX = np.asarray(XX)

    Y = [item for sublist in tempY for item in sublist]

    niter = 0
    X = []

    for y in tempY:
        for item in y:
            X.append(tempX[niter])
        niter = niter + 1

    guess_mean = np.mean(Y)
    guess_std = 3 * np.std(Y) / (2 ** 0.5)
    guess_phase = 0
    X = np.asarray(X)

    data_first_guess = guess_std * np.sin(X + guess_phase) + guess_mean
    optimize_func = lambda x: x[0] * np.sin(X + x[1]) + x[2] - Y
    est_std, est_phase, est_mean = leastsq(optimize_func, [guess_std, guess_phase, guess_mean])[0]
    data_fit = est_std * np.sin(X + est_phase) + est_mean

    data_first_guessXX = guess_stdXX * np.sin(XX + guess_phaseXX) + guess_meanXX
    optimize_funcXX = lambda x: x[0] * np.sin(XX + x[1]) + x[2] - YY
    est_stdXX, est_phaseXX, est_meanXX = leastsq(optimize_funcXX, [guess_stdXX, guess_phaseXX, guess_meanXX])[0]
    data_fitXX = est_stdXX * np.sin(XX + est_phaseXX) + est_meanXX

    return data_fitXX.min(), data_fitXX.max(), data_fitXX.max()-data_fitXX.min(), (data_fitXX.max()-data_fitXX.min()) / np.abs(data_fitXX.min())

    # return data_fitXX.max()-data_fitXX.min(), (data_fitXX.max()-data_fitXX.min()) / np.abs(data_fitXX.min())
