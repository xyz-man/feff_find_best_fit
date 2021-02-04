'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 11.01.2021
'''
from pkg_lib.pkg_bases.class_ExtendBase import ExtendBase
from pkg_lib.pkg_bases.class_two_spectrums import *
from pkg_lib.pkg_files.load_list_of_feff_files import *
from hashlib import sha256

from typing import NewType


CurveType = NewType("CurveType", Curve)


class SubMultiCurve(ExtendBase):
    def __init__(self):
        super(SubMultiCurve, self).__init__()
        self.working_directory_path = Configuration.PATH_TO_THEORY_SPECTRA_DIRECTORY

        # the word by which the full path to the file will be cut and the curve name will be created
        self.cut_part_of_file_name = 'Ira'

        self.figure = None
        self.figure_manager = None
        self.axes = None
        self.out_directory_name = None

        self.current_id = None
        self.current_file_name = None
        self.current_name = None
        self.current_hash = None

        self.current_group_id = None
        self.current_group_name = None
        self.current_group_mask = None

        self.current_model_name = None
        self.current_model_path = None

        self.current_curve = Curve()
        self.current_curve.label.x = 'Energy,[eV]'
        self.current_curve.label.y = 'Intensity,[a.u.]'

        # set limits for create interpolation energy (x- coordinates) for loaded spectra
        #  do not use:
        self.max_of_minimum_energy_point = -1e6
        self.min_of_maximum_energy_point = 1e6
        self.number_of_energy_points = 100

        self.dict_of_theoretical_curves = odict()
        # the linker between tha groups name and the sub-folder names (for multigroup fitting, class MultiGroupCurve):
        self.group_name_and_mask_linker_dict = None

        self.out_directory_name = None

    def flush(self):
        self.figure = None
        self.figure_manager = None
        self.axes = None
        self.out_directory_name = None

        self.current_id = None
        self.current_file_name = None
        self.current_name = None
        self.current_hash = None
        self.current_group_id = None
        self.current_group_name = None
        self.current_group_mask = None
        self.current_model_name = None
        self.current_model_path = None
        self.current_curve = Curve()
        self.current_curve.label.x = 'Energy,[eV]'
        self.current_curve.label.y = 'Intensity,[a.u.]'
        self.dict_of_theoretical_curves = odict()
        self.group_name_and_mask_linker_dict = None

    def get_hash(self, val=None):
        out = None
        if val is not None:
            out = sha256(val.encode('utf-8')).hexdigest()
        return out

    def load_curves_to_dict_of_theoretical_curves(self):
        spectra_dict = get_dict_of_spectra_filenames_and_prepared_names_from_dir(
            dir_path=self.working_directory_path,
            cut_dir_name=self.cut_part_of_file_name,
            group_name_and_mask_dict=self.group_name_and_mask_linker_dict
        )
        # leave only those filenames which consists specific text
        i = 0
        for key, val in spectra_dict.items():
            self.current_id = i
            self.current_file_name = val['filename']
            self.current_name = val['name']
            self.current_group_id = val['group_id']
            self.current_group_name = val['group_name']
            self.current_group_mask = val['group_mask']
            self.current_model_name = val['model_name']
            self.current_model_path = val['model_path']
            if self.current_group_name is None:
                self.current_hash = self.get_hash(val=self.current_file_name)
            else:
                self.current_hash = self.get_hash(val=self.current_model_path)

            self.current_curve.src_coordinate.x, self.current_curve.src_coordinate.y = \
                load_theoretical_xmu_data(self.current_file_name)

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

            self.current_curve.curve_label_latex = '{nm}'.format(
                id=self.current_id,
                nm=self.current_name,
            )

            tmp_dict = odict()
            tmp_dict['id'] = deepcopy(self.current_id)
            tmp_dict['hash'] = self.current_hash
            tmp_dict['filename'] = self.current_file_name
            tmp_dict['name'] = self.current_name

            tmp_dict['group_id'] = self.current_group_id
            tmp_dict['group_name'] = self.current_group_name
            tmp_dict['group_mask'] = self.current_group_mask
            tmp_dict['model_name'] = self.current_model_name
            tmp_dict['model_path'] = self.current_model_path

            tmp_dict['curve'] = deepcopy(self.current_curve)
            self.dict_of_theoretical_curves[key] = tmp_dict

            i = i + 1

            # self.current_curve.plot_curve(axes=self.axes)
            # plt.draw()

    def plot_curves(self):
        for key, val in self.dict_of_theoretical_curves.items():
            val['curve'].plot_curve(axes=self.axes)


if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')
    obj = SubMultiCurve()
    obj.working_directory_path = '/home/yugin/PycharmProjects/feff_find_best_fit/data/tmp_theoretical/Ira/'
    obj.flush()
    obj.setup_axes()
    obj.load_experimental_curve()
    obj.load_curves_to_dict_of_theoretical_curves()
    obj.plot_curves()
    plt.legend()
    plt.show(block=True)
    # plt.pause(3)
    print('stop')
