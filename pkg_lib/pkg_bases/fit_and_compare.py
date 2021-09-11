'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 11.01.2021
'''
import os
from pprint import pprint
from pkg_lib.pkg_bases.class_average_curves import *
from pathlib import PurePosixPath
# from pkg_lib.pkg_files.dir_and_file_operations import


class TwoSpectraLinearFit(BaseClass):
    def __init__(self):
        self.working_directory_path = Configuration.PATH_TO_THEORY_SPECTRA_DIRECTORY
        self.cut_part_of_file_name = 'None'

        self.experimental_curve = Curve()

        self.figure = plt.figure()
        self.out_directory_name = None

        # curve #1:
        self.curve_1_current_id = None
        self.curve_1_current_file_name = None
        self.curve_1_current_curve = Curve()
        self.curve_1_current_curve.label.x = 'Energy,[eV]'
        self.curve_1_current_curve.label.y = 'Intensity,[a.u.]'

        # curve #2:
        self.curve_2_current_id = None
        self.curve_2_current_file_name = None
        self.curve_2_current_curve = Curve()
        self.curve_2_current_curve.label.x = 'Energy,[eV]'
        self.curve_2_current_curve.label.y = 'Intensity,[a.u.]'

        # set limits for create interpolation energy (x- coordinates) for loaded spectra
        #  do not use:
        self.max_of_minimum_energy_point = -1e6
        self.min_of_maximum_energy_point = 1e6
        self.number_of_energy_points = 100

        self.dict_of_theoretical_curves = odict()

        self.averaging_curve = DoubleCurves()
        self.list_of_unique_distance = []
        # max distance to create average spectra:
        self.average_distance = 15
        self.number_of_spectra_for_average = 0
        # this number is needed to calculate the average spectra, so we summarize twice all the spectra for which the
        # distance is less than the maximum and only once the spectra for this maximum distance.
        self.max_distance_in_selected_spectra = 0
        self.array_of_theoretical_y_coordinates = None
        # result spectrum of averaging procedure:
        self.result_average_y = None


if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')

