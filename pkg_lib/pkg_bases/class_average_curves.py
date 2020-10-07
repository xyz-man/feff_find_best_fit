'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 16.09.2020
'''
import logging
import pickle
import dill
import pandas as pd
import io
import os
from pkg_lib.pkg_bases.class_two_spectrums import *
from pkg_lib.pkg_files.dir_and_file_operations import create_out_data_folder


class RenameUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        renamed_module = module
        if module == "cfg.class_cfg":
            renamed_module = "lib_tmp_pkg.class_cfg"
        if module == "lib_pkg.bases_stored_config":
            renamed_module = "lib_tmp_pkg.bases_stored_config"

        return super(RenameUnpickler, self).find_class(renamed_module, name)


def renamed_load(file_obj):
    return RenameUnpickler(file_obj).load()


def renamed_loads(pickled_bytes):
    file_obj = io.BytesIO(pickled_bytes)
    return renamed_load(file_obj)


class AverageCurves(BaseClass):
    def __init__(self):
        self.working_directory_path = Configuration.PATH_TO_THEORY_SPECTRA_DIRECTORY
        self.file_name_of_stored_vars = Configuration.STORED_VARIABLES_OF_THEORETICAL_CALCULATED_SPECTRA_FILE_NAME
        self.stored_vars_data = None

        self.experimental_curve = Curve()

        self.figure = plt.figure()
        self.out_directory_name = None

        self.current_id = None
        self.current_distance = None
        self.current_polarization = None
        self.current_dir_name = None
        self.current_curve = Curve()
        self.current_curve.label.x = 'Energy,[eV]'
        self.current_curve.label.y = 'Intensity,[a.u.]'

        # set limits for create interpolation energy (x- coordinates) for loaded spectra
        #  do not use:
        self.max_of_minimum_energy_point = -1e6
        self.min_of_maximum_energy_point = 1e6
        self.number_of_energy_points = 100

        self.dict_of_theoretical_curves = odict()

        self.averaging_curve = DoubleCurves()
        self.list_of_unique_distance = []
        # max distance to create average spectra:
        self.average_distance = 10
        self.number_of_spectra_for_average = 0
        # this number is needed to calculate the average spectra, so we summarize twice all the spectra for which the
        # distance is less than the maximum and only once the spectra for this maximum distance.
        self.max_distance_in_selected_spectra = 0
        self.array_of_theoretical_y_coordinates = None
        # result spectrum of averaging procedure:
        self.result_average_y = None

    def flush(self):
        self.averaging_curve = DoubleCurves()
        self.array_of_theoretical_y_coordinates = None

    def load_data_from_pickle_file(self):
        if os.path.isfile(os.path.join(self.working_directory_path, self.file_name_of_stored_vars)):
            pckl_file = os.path.join(self.working_directory_path, self.file_name_of_stored_vars)
            with open(pckl_file, 'rb') as f:
                # obj = pickle.load(f)
                obj = renamed_load(f)
            # print('')
            try:
                self.stored_vars_data = obj[0]
            except Exception as err:
                error_txt = 'AverageCurves: load_data_from_pickle_file: \n'
                error_txt = error_txt + '{} does not have stored vars\n'.format(
                    self.file_name_of_stored_vars)
                logging.getLogger("error_logger").error(error_txt + repr(err))
                if Configuration.DEBUG:
                    print(error_txt, repr(err))

    def load_experimental_curve(self):
        data = load_experimental_data()
        self.experimental_curve.src_coordinate.x = data[:, 0]
        self.experimental_curve.src_coordinate.y = data[:, 1]
        self.experimental_curve.curve_label_latex = 'ZnO-0deg'
        self.experimental_curve.label.x = 'Energy,[eV]'
        self.experimental_curve.label.y = 'Intensity,[a.u.]'
        # self.experimental_curve.plot_curve()
        # plt.draw()

        # self.experimental_curve.src_coordinate.x = data[:, 0]
        # self.experimental_curve.src_coordinate.y = data[:, 2]
        # self.experimental_curve.curve_label_latex = 'ZnO-45deg'
        # self.experimental_curve.plot_curve()
        # plt.draw()
        #
        # self.experimental_curve.src_coordinate.x = data[:, 0]
        # self.experimental_curve.src_coordinate.y = data[:, 3]
        # self.experimental_curve.curve_label_latex = 'ZnO-75deg'
        # self.experimental_curve.plot_curve()
        # plt.draw()

    def load_curves_to_dict(self):
        if self.stored_vars_data is not None:
            for key, val in self.stored_vars_data.list_of_variable_dicts.items():
                self.current_id = val.dict_of_stored_vars['id']
                self.current_distance = val.dict_of_stored_vars['distance']
                self.list_of_unique_distance.append(self.current_distance)

                if self.current_distance <= self.average_distance:
                    self.number_of_spectra_for_average = self.number_of_spectra_for_average + 1
                    self.max_distance_in_selected_spectra = self.current_distance

                self.current_dir_name = val.dict_of_stored_vars['directory_name']
                file_path = os.path.join(self.working_directory_path, self.current_dir_name, 'xmu.dat')
                self.current_curve.src_coordinate.x, self.current_curve.src_coordinate.y = \
                    load_theoretical_xmu_data(file_path)

                min_energy_point = min(self.current_curve.src_coordinate.x)
                max_energy_point = max(self.current_curve.src_coordinate.x)
                num_energy_points = np.size(self.current_curve.src_coordinate.x)

                if num_energy_points > self.number_of_energy_points:
                    print("Energy Points change: {old} -> {new}".format(old=self.number_of_energy_points,
                                                                new=num_energy_points))
                    self.number_of_energy_points = num_energy_points

                if self.max_of_minimum_energy_point < min_energy_point:
                    print("Max of min change: {old} -> {new}".format(old=self.max_of_minimum_energy_point,
                                                             new=min_energy_point))
                    self.max_of_minimum_energy_point = min_energy_point

                if self.min_of_maximum_energy_point > max_energy_point:
                    print("Min of max change: {old} -> {new}".format(old=self.min_of_maximum_energy_point,
                                                             new=max_energy_point))
                    self.min_of_maximum_energy_point = max_energy_point

                self.current_curve.curve_label_latex = '{id}:{dst}'.format(
                    id=self.current_id,
                    dst=self.current_distance,
                )

                tmp_dict = odict()
                tmp_dict['id'] = deepcopy(self.current_id)
                tmp_dict['distance'] = self.current_distance
                tmp_dict['directory_name'] = self.current_dir_name
                tmp_dict['curve'] = deepcopy(self.current_curve)
                self.dict_of_theoretical_curves[key] = tmp_dict

                # self.current_curve.plot_curve()
                # plt.draw()

            self.list_of_unique_distance = np.unique(self.list_of_unique_distance)
            print(self.list_of_unique_distance)

    def create_average_spectrum(self):
        if self.dict_of_theoretical_curves is not None:
            num_of_spectra = 0
            self.averaging_curve.ideal_curve = self.experimental_curve

            x_step = (self.min_of_maximum_energy_point -
                      self.max_of_minimum_energy_point)/(self.number_of_energy_points + 1)
            x_interp = np.r_[
                       self.max_of_minimum_energy_point:self.min_of_maximum_energy_point:x_step]

            for key, val in self.dict_of_theoretical_curves.items():
                distance = val['distance']
                if distance <= self.average_distance:

                    self.current_id = val['id']
                    self.current_distance = distance
                    self.current_dir_name = val['directory_name']
                    self.current_curve = None
                    self.current_curve = val['curve']

                    # x_old = self.current_curve.src_coordinate.x
                    # y_old = self.current_curve.src_coordinate.y
                    # y_new = np.interp(x_interp, x_old, y_old)

                    # self.averaging_curve.probe_curve.src_coordinate.x = x_interp
                    # self.averaging_curve.probe_curve.src_coordinate.y = y_new
                    # self.averaging_curve.update_variables()
                    # self.averaging_curve.plot_probe_curve()

                    self.averaging_curve.probe_curve = deepcopy(self.current_curve)
                    self.averaging_curve.update_variables()

                    if self.array_of_theoretical_y_coordinates is None and (num_of_spectra < 1):
                        # initiate the size of array_of_theoretical_y_coordinates:
                        self.array_of_theoretical_y_coordinates = \
                            self.averaging_curve.probe_curve.new_coordinate.y
                    else:
                        if distance < self.max_distance_in_selected_spectra:
                            # summarize twice for spectra for which the distance is less than the maximum:
                            self.array_of_theoretical_y_coordinates = np.vstack(
                                (
                                    self.array_of_theoretical_y_coordinates,
                                    self.averaging_curve.probe_curve.new_coordinate.y,
                                )
                            )
                            self.array_of_theoretical_y_coordinates = np.vstack(
                                (
                                    self.array_of_theoretical_y_coordinates,
                                    self.averaging_curve.probe_curve.new_coordinate.y,
                                )
                            )

                        if distance == self.max_distance_in_selected_spectra:
                            # summarize only once the spectra for this maximum distance:
                            self.array_of_theoretical_y_coordinates = np.vstack(
                                (
                                    self.array_of_theoretical_y_coordinates,
                                    self.averaging_curve.probe_curve.new_coordinate.y,
                                )
                            )
                    print(np.shape(self.array_of_theoretical_y_coordinates))

                    num_of_spectra = num_of_spectra + 1
                    # print(num_of_spectra)

            try:
                m, n = np.shape(self.array_of_theoretical_y_coordinates)
                self.result_average_y = np.average(self.array_of_theoretical_y_coordinates, axis=0)
                print(self.result_average_y - self.averaging_curve.probe_curve.src_coordinate.y)
                self.averaging_curve.probe_curve.src_coordinate.y = self.result_average_y

            except Exception:
                m = 1
                self.averaging_curve.probe_curve.src_coordinate.y = self.array_of_theoretical_y_coordinates

            self.averaging_curve.probe_curve.curve_label_latex = '<n={} spectra>, d={}'\
                .format(m, self.current_distance)
            self.averaging_curve.plot_two_curves()

            self.averaging_curve.show_optimum()
            self.averaging_curve.probe_curve.curve_label = 'n={} spectra d={}'\
                .format(m, self.current_distance)
            self.averaging_curve.out_directory_name = self.out_directory_name
            self.averaging_curve.save_curves_to_ascii_file()
            self.averaging_curve.save_figure_to_png()

    def generate_average_spectra(self):
        self.out_directory_name = create_out_data_folder(
            main_folder_path=self.working_directory_path,
            first_part_of_folder_name='aver',
        )
        for val in self.list_of_unique_distance:
            self.average_distance = val + 0.0001
            self.flush()
            self.create_average_spectrum()


if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')
    import tkinter as tk
    from tkinter import filedialog
    from pkg_lib.pkg_files.class_store_and_load_vars import StoreAndLoadVars

    obj_path = StoreAndLoadVars()
    print('last used: {}'.format(obj_path.get_last_used_dir_path()))
    # openfile dialoge
    root = tk.Tk()
    root.withdraw()
    dir_path = filedialog.askdirectory(initialdir=obj_path.get_last_used_dir_path())
    if os.path.isdir(dir_path):
        obj_path.last_used_dir_path = dir_path
        obj_path.save_last_used_dir_path()
        print('last used: {}'.format(obj_path.get_last_used_dir_path()))
    obj = AverageCurves()
    obj.working_directory_path = obj_path.get_last_used_dir_path()
    obj.load_data_from_pickle_file()
    print(obj.stored_vars_data)
    obj.load_experimental_curve()
    obj.load_curves_to_dict()
    # obj.create_average_spectrum()
    obj.generate_average_spectra()
    # plt.legend()
    # plt.show()