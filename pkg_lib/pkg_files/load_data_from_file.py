'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 14.09.2020
'''
import os
from pkg_lib.pkg_cfg.class_configure import Configuration
import numpy as np


def load_theoretical_xmu_data(file_path):
    data = np.loadtxt(file_path, float)
    x_old = data[:, Configuration.THEORETICAL_SPECTRUM_COLUMN_NUMBER_X]
    y_old = data[:, Configuration.THEORETICAL_SPECTRUM_COLUMN_NUMBER_Y]
    x_new = Configuration.SPECTRUM_CALCULATION_X_REGION
    y_new = np.interp(x_new, x_old, y_old)
    return x_new, y_new


def load_experimental_data():
    # load experimental xmu-data file. In  non-existent points we use linear interp procedure
    data = np.loadtxt(Configuration.PATH_TO_EXPERIMENT_SPECTRA_FILE, float)
    data[:, 0] = data[:, 0] + Configuration.EXPERIMENTAL_SPECTRUM_X_SHIFT
    x_old = data[:, 0]
    x_new = Configuration.SPECTRUM_CALCULATION_X_REGION
    new_data = np.zeros((len(x_new), 4))
    new_data[:, 0] = x_new
    for i in range(1, 4):
        data[:, i] = Configuration.EXPERIMENTAL_SPECTRUM_Y_SCALE * data[:, i] + \
                     Configuration.EXPERIMENTAL_SPECTRUM_Y_SHIFT
        y_old = data[:, i]
        y_new = np.interp(x_new, x_old, y_old)
        new_data[:, i] = y_new

    return new_data


if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')
    file_path1 = r'/mnt/nfsv4/abel_share/free_share/ZnO/ZnO_ideal_p=[100]_0001/xmu.dat'
    file_path2 = r'/mnt/nfsv4/abel_share/free_share/ZnO/ZnO_ideal_p=[101]_0001/xmu.dat'
    file_path3 = r'/mnt/nfsv4/abel_share/free_share/ZnO/ZnO_ideal_p=[103]_0001/xmu.dat'
    exp_data_path2 = os.path.join(
        Configuration.PATH_TO_LOCAL_DATA_DIRECTORY, 'experiment', 'experiment_ZnO_O-Kedge_[0,45,75].dat')
    chi1 = load_theoretical_xmu_data(file_path1)
    chi2 = load_theoretical_xmu_data(file_path2)
