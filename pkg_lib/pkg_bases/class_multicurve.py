'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 11.01.2021
'''
from loguru import logger
from pkg_lib.pkg_bases.class_sub_multicurve import *
import matplotlib.gridspec as gridspec
import itertools
from scipy.optimize import minimize, minimize_scalar
from scipy.optimize import differential_evolution
from pprint import pprint
from pkg_lib.pkg_files.dir_and_file_operations import *
import shutil


def get_list_without_duplicates(input_list=None):
    out = None
    if input_list is not None:
        out = list(set(input_list))
    return out


def remove_duplicates_from_list_of_tuples(lst):
    return [t for t in (set(tuple(sorted(i)) for i in lst))]


class MultiCurve(ExtendBase):
    '''
    you need to define a way to calculate the hash key value.
    By default, the hash is calculated from the full filename in SubMultiCurve.get_hash()
    '''
    def __init__(self):
        super(MultiCurve, self).__init__()
        self.list_of_theoretical_spectra_directory_path = []
        # the word by which the full path to the file will be cut and the curve name will be created
        self.list_of_cut_parts_of_file_name = []

        self.number_of_curve_directory_paths_for_fit = None

        self.current_multi_curve = SubMultiCurve()
        self.r_factor_region = Configuration.SPECTRUM_CALCULATION_R_FACTOR_REGION

        # set limits for create interpolation energy (x- coordinates) for loaded spectra
        #  do not use:
        self.max_of_minimum_energy_point = -1e6
        self.min_of_maximum_energy_point = 1e6
        self.number_of_energy_points = 100

        # the dict of the self.number_of_curves_for_fit of curves for optimizing:
        self.dict_of_multi_curves_for_processing = odict()
        self.dict_of_hash_and_curves_combinations_for_processing = odict()
        self.list_of_hash_combinations = None
        self.minimization_method = 'differential_evolution'
        # self.minimization_method = 'minimize'
        # variables for processing for each step of calculations:
        self.current_hash_list = None
        self.current_theoretical_y_coordinates = None
        self.current_experimental_y_coordinates_in_r_factor_region = None
        self.current_theoretical_y_coordinates_in_r_factor_region = None
        self.current_r_factor = None
        self.current_sigma_squared = None
        self.current_optimized_params = None
        self.current_txt = None
        self.current_label = None
        self.current_out_directory_name = None
        self.current_out_file_name = None

        self.global_minimum_r_factor = 10

        self.dict_of_results = odict()

        self.out_directory_name = None

    def flush(self):
        self.list_of_theoretical_spectra_directory_path = []
        self.list_of_cut_parts_of_file_name = []
        self.number_of_curve_directory_paths_for_fit = None
        self.current_multi_curve = SubMultiCurve()
        self.max_of_minimum_energy_point = -1e6
        self.min_of_maximum_energy_point = 1e6
        self.number_of_energy_points = 100
        self.dict_of_multi_curves_for_processing = odict()
        self.dict_of_results = None
        self.result_average_y = None
        self.optimized_params = []
        self.out_directory_name = None

        self.current_hash_list = None
        self.current_theoretical_y_coordinates = None
        self.current_r_factor = None

    def setup_axes(self):
        plt.ion()  # Force interactive
        plt.close('all')
        plt.switch_backend('QT5Agg', )
        plt.rc('font', family='serif')
        self.figure = plt.figure(figsize=(np.array(Configuration.FIGURE_GEOMETRY[2:]))/Configuration.DPI)
        self.figure_manager = plt.get_current_fig_manager()
        gspec = gridspec.GridSpec(
            nrows=self.number_of_curve_directory_paths_for_fit, ncols=2, figure=self.figure)

        self.axes = list()
        # add main subplot axes for fit result:
        self.axes.append(self.figure.add_subplot(gspec[:, 0]))
        # add subplots for each sub-multicurve:
        for i in range(self.number_of_curve_directory_paths_for_fit):
            self.axes.append(self.figure.add_subplot(gspec[i, 1]))

        for val in self.axes:
            for axis in ['top', 'bottom', 'left', 'right']:
                val.spines[axis].set_linewidth(2)
        # for axis in ['top', 'bottom', 'left', 'right']:
        #     self.axes[0].spines[axis].set_linewidth(2)
        # plt.subplots_adjust(top=0.85)
        # gs1.tight_layout(fig, rect=[0, 0.03, 1, 0.95])
        self.figure.tight_layout(rect=[0.03, 0.03, 1, 0.9], w_pad=1.1)

        # put window to the second monitor
        # figManager.window.setGeometry(1923, 23, 640, 529)
        self.figure_manager.window.setGeometry(*Configuration.FIGURE_GEOMETRY)
        # self.figure_manager.window.setWindowTitle(window_title)
        self.figure_manager.window.showMinimized()

        # plt.show()
        # ax.plot( x, y, label = '<$\chi(k)$>' )
        # ax.plot( x, y_median, label = '$\chi(k)$ median', color = 'darkcyan')
        # ax.plot( x, y_max, label = '$\chi(k)$ max', color = 'skyblue' )
        # ax.plot( x, y_min, label = '$\chi(k)$ min', color = 'lightblue' )


    def get_current_sub_multi_curve_by_id(self, idx=None):
        out = None
        if idx is not None:
            out = SubMultiCurve()
            # set the energy values and number of points:
            out.max_of_minimum_energy_point = self.max_of_minimum_energy_point
            out.min_of_maximum_energy_point = self.min_of_maximum_energy_point
            out.number_of_energy_points = self.number_of_energy_points

            out.load_experimental_curve()
            # set the cut part name and directory path:
            out.cut_part_of_file_name = self.list_of_cut_parts_of_file_name[idx]
            out.working_directory_path = self.list_of_theoretical_spectra_directory_path[idx]
            # load curves from selected directory:
            out.load_curves_to_dict_of_theoretical_curves()
        return out

    def load_curves_to_dict_of_multi_curves_for_processing(self):
        # check the max_of_minimum_energy_point, min_of_maximum_energy_point and number_of_energy_points:
        if self.number_of_curve_directory_paths_for_fit > 0:
            for i in range(self.number_of_curve_directory_paths_for_fit):
                self.current_multi_curve = self.get_current_sub_multi_curve_by_id(idx=i)

                min_energy_point = self.current_multi_curve.max_of_minimum_energy_point
                max_energy_point = self.current_multi_curve.min_of_maximum_energy_point
                num_energy_points = self.current_multi_curve.number_of_energy_points

                if num_energy_points > self.number_of_energy_points:
                    print("Energy Points change: {old} -> {new}".format(
                        old=self.number_of_energy_points,
                        new=num_energy_points))
                    self.number_of_energy_points = num_energy_points

                if self.max_of_minimum_energy_point < min_energy_point:
                    print("Max of min change: {old} -> {new}".format(
                        old=self.max_of_minimum_energy_point,
                        new=min_energy_point))
                    self.max_of_minimum_energy_point = min_energy_point

                if self.min_of_maximum_energy_point > max_energy_point:
                    print("Min of max change: {old} -> {new}".format(
                        old=self.min_of_maximum_energy_point,
                        new=max_energy_point))
                    self.min_of_maximum_energy_point = max_energy_point

            # repeat loading curves with a new values of
            # max_of_minimum_energy_point, min_of_maximum_energy_point and number_of_energy_points:
            Configuration.SPECTRUM_CALCULATION_X_MIN = self.max_of_minimum_energy_point
            Configuration.SPECTRUM_CALCULATION_X_MAX = self.min_of_maximum_energy_point
            x_step = (self.min_of_maximum_energy_point -
                      self.max_of_minimum_energy_point) / (self.number_of_energy_points + 1)
            Configuration.SPECTRUM_CALCULATION_X_STEP_SIZE = x_step
            Configuration.create_calculation_region()

            self.load_experimental_curve()
            for i in range(self.number_of_curve_directory_paths_for_fit):
                self.current_multi_curve = self.get_current_sub_multi_curve_by_id(idx=i)

                # put current multicurve into the dict:
                tmp_dict = odict()
                tmp_dict['id'] = i
                tmp_dict['curves'] = deepcopy(self.current_multi_curve)
                self.dict_of_multi_curves_for_processing[i] = tmp_dict

                self.current_multi_curve.axes = self.axes[i+1]
                self.current_multi_curve.plot_curves()
                self.current_multi_curve.axes.set_title(
                    self.list_of_cut_parts_of_file_name[i]
                )
                plt.legend()
                plt.draw()
                plt.show()

    # def get_points_for_experimental_curve_in_region(self):
    #     x_vector = self.experimental_curve.src_coordinate.x
    #     y_vector = self.experimental_curve.src_coordinate.y
    #
    #     out_x, out_y, y_in_r_region, index_min, index_max = get_points_and_indices_in_region(
    #         x_vector=x_vector,
    #         y_vector=y_vector,
    #         r_factor_region=self.r_factor_region,
    #     )
    #     self.current_experimental_y_coordinates_in_r_factor_region = y_in_r_region
    #     return out_x, out_y, y_in_r_region, index_min, index_max

    def get_points_for_experimental_curve_in_region(self):
        x_vector = self.experimental_curve.src_coordinate.x
        y_vector = copy(self.experimental_curve.src_coordinate.y)

        out_x, out_y, y_in_r_region, index_min, index_max = get_points_and_indices_in_region(
            x_vector=x_vector,
            y_vector=y_vector,
            r_factor_region=self.r_factor_region,
        )
        self.current_experimental_y_coordinates_in_r_factor_region = y_in_r_region
        return out_x, out_y, y_in_r_region, index_min, index_max

    def get_points_for_current_theoretical_curve_in_region(self):
        x_vector = self.experimental_curve.src_coordinate.x
        y_vector = copy(self.current_theoretical_y_coordinates)

        out_x, out_y, y_in_r_region, index_min, index_max = get_points_and_indices_in_region(
            x_vector=x_vector,
            y_vector=y_vector,
            r_factor_region=self.r_factor_region,
        )
        self.current_theoretical_y_coordinates_in_r_factor_region = y_in_r_region
        return out_x, out_y, y_in_r_region, index_min, index_max

    def get_r_factor(self):
        y_ideal = self.current_experimental_y_coordinates_in_r_factor_region
        # update values of theoretical data:
        self.get_points_for_current_theoretical_curve_in_region()
        y_probe = self.current_theoretical_y_coordinates_in_r_factor_region
        if (y_ideal is not None) and (y_probe is not None):
            self.current_r_factor = get_r_factor_numba_v(np.asarray(y_ideal, dtype=float),
                                                         np.asarray(y_probe, dtype=float))
            return self.current_r_factor
        else:
            return None

    def get_sigma_squared(self):
        '''
        return unbiased sample variance of vector
        :return:
        '''
        s2 = None
        y_ideal = self.current_experimental_y_coordinates_in_r_factor_region
        # update values of theoretical data:
        self.get_points_for_current_theoretical_curve_in_region()
        y_probe = self.current_theoretical_y_coordinates_in_r_factor_region
        # replace by numba:
        if (y_ideal is not None) and (y_probe is not None):
            s2 = np.sum((y_ideal - y_probe) ** 2) / (len(y_ideal) - 1)
        self.current_sigma_squared = s2
        return s2

    def get_dict_of_hash_and_curves_combinations_for_processing(self):
        '''
        create dict of hash - curves
        :return: hash - curve  dict
        '''
        for key, val in self.dict_of_multi_curves_for_processing.items():
            for key_in, val_in in val['curves'].dict_of_theoretical_curves.items():
                try:
                    self.dict_of_hash_and_curves_combinations_for_processing[val_in['hash']] = val_in['curve']
                except:
                    pass
        return self.dict_of_hash_and_curves_combinations_for_processing

    def get_curve_by_hash(self, hash=None):
        out = None
        try:
            out = self.dict_of_hash_and_curves_combinations_for_processing[hash]
        except:
            pass
        return out

    def get_hash_list_of_curves_combinations(self):
        '''
        create list of curve hashes combinations for processing
        [('hash11', 'hash21'), ('hash11', 'hash22'),...]
        :return:
        '''
        result_hash_list = []
        for key, val in self.dict_of_multi_curves_for_processing.items():
            tmp_hash_list = []
            for key_in, val_in in val['curves'].dict_of_theoretical_curves.items():
                tmp_hash_list.append(val_in['hash'])
            tmp_hash_list.sort()
            result_hash_list.append(tmp_hash_list)

        result_hash_list_combinations = list(itertools.product(*result_hash_list))
        logger.info(len(result_hash_list_combinations))

        result_hash_list_combinations_without_duplicates = []
        for lst in result_hash_list_combinations:
            try:
                if len(get_list_without_duplicates(input_list=lst)) == self.number_of_curve_directory_paths_for_fit:
                    result_hash_list_combinations_without_duplicates.append(lst)
            except:
                pass
        result_hash_list_combinations_without_duplicates = remove_duplicates_from_list_of_tuples(
            result_hash_list_combinations_without_duplicates)
        logger.info(len(result_hash_list_combinations_without_duplicates))
        # logger.info(result_hash_list_combinations_without_duplicates)

        self.list_of_hash_combinations = result_hash_list_combinations_without_duplicates
        return result_hash_list_combinations_without_duplicates

    def func_for_optimize(self, x):
        # create function of snapshots linear composition Sum[x_i*F_i]
        num = self.number_of_curve_directory_paths_for_fit
        x = np.abs(x)
        tmp_y_vector = []
        sum_x = np.sum(x)

        for i, hash in enumerate(self.current_hash_list):
            if abs(sum_x) > 0:
                k = x[i] / sum_x
            else:
                k = x[i]

            if i < 1:
                tmp_y_vector = k * self.get_curve_by_hash(hash=hash).src_coordinate.y

            else:
                tmp_y_vector = tmp_y_vector + k * self.get_curve_by_hash(hash=hash).src_coordinate.y

        return tmp_y_vector

    def run_fit_procedure_for_current_values(self):
        num = self.number_of_curve_directory_paths_for_fit
        x0 = np.zeros(num)
        # create bounds:
        bounds = []
        for i in x0:
            bounds.append((0, 1))

        def func(x):
            self.current_theoretical_y_coordinates = self.func_for_optimize(x)
            self.get_r_factor()
            return self.current_r_factor

        # res_tmp = func(x0)
        if self.minimization_method == 'minimize':
            res = minimize(func, x0=x0, bounds=bounds, options={'gtol': 1e-8, 'disp': True})
        elif self.minimization_method == 'differential_evolution':
            res = differential_evolution(func, bounds, tol=1e3)

        if np.sum(res.x) > 0:
            self.current_optimized_params = res.x / np.sum(res.x)
        else:
            self.current_optimized_params = res.x

    def run_fit_procedure(self):
        # generate list of tuples of hashes:
        self.get_hash_list_of_curves_combinations()
        # generate special form of dict for quick data access by hash:
        self.get_dict_of_hash_and_curves_combinations_for_processing()
        # prepare data from experimental curve:
        self.get_points_for_experimental_curve_in_region()
        for num, val_lst in enumerate(self.list_of_hash_combinations):
            self.current_hash_list = val_lst
            self.run_fit_procedure_for_current_values()
            self.get_sigma_squared()
            if self.is_global_minimum_r_factor():
                tmp_dict = odict()
                tmp_dict['r_factor'] = deepcopy(self.current_r_factor)
                tmp_dict['sigma_squared'] = deepcopy(self.current_sigma_squared)
                tmp_dict['hash_list'] = deepcopy(self.current_hash_list)
                tmp_dict['optimized_params'] = deepcopy(self.current_optimized_params)
                tmp_dict['x_coordinates'] = deepcopy(self.experimental_curve.src_coordinate.x)
                tmp_dict['experimental_y_coordinates'] = deepcopy(self.experimental_curve.src_coordinate.y)
                tmp_dict['experimental_y_coordinates_in_r_factor_region'] = \
                    deepcopy(self.current_experimental_y_coordinates_in_r_factor_region)
                tmp_dict['theoretical_y_coordinates'] = deepcopy(self.current_theoretical_y_coordinates)
                tmp_dict['theoretical_y_coordinates_in_r_factor_region'] = \
                    deepcopy(self.current_theoretical_y_coordinates_in_r_factor_region)

                self.dict_of_results[num] = tmp_dict

                self.current_txt = None
                self.current_txt = 'R={rf:1.7f}, $\sigma^2$={sq:1.7f}\n'.format(
                    rf=self.current_r_factor,
                    sq=self.current_sigma_squared,
                )
                self.current_label = ''
                # plot curves
                for i, hs in enumerate(self.current_hash_list):
                    current_curve = self.get_curve_by_hash(hs)
                    # generate txt string:
                    self.current_label = self.current_label + '{0} x [ '.format(
                        round(self.current_optimized_params[i], 5)
                    ) + current_curve.curve_label_latex + ' ]'
                    if i < len(self.current_optimized_params) - 1:
                        self.current_label = self.current_label + ' + \n'
                    current_curve.axes = self.axes[i + 1]
                    plt.axes(current_curve.axes)
                    plt.cla()
                    self.experimental_curve.axes = self.axes[i + 1]
                    current_curve.plot_curve()
                    # self.experimental_curve.is_src_plotted = True
                    self.experimental_curve.plot_curve()
                    plt.legend()
                    plt.draw()
                    plt.show()

                self.current_txt = self.current_txt + self.current_label
                self.plot_fit_resulted_curves()
                plt.legend()
                plt.draw()
                plt.show()
                self.save_current_curves_to_ascii_and_png_files()
        # copy the global minimum files into up directory:
        if self.current_out_file_name is not None:
            source = self.current_out_directory_name
            destination = self.out_directory_name
            shutil.copytree(source, destination, dirs_exist_ok=True)

    def is_global_minimum_r_factor(self):
        if self.current_r_factor <= self.global_minimum_r_factor:
            self.global_minimum_r_factor = copy(self.current_r_factor)
            return True
        else:
            return False

    def plot_fit_resulted_curves(self):
        axes = self.axes[0]
        plt.axes(axes)
        plt.cla()
        self.experimental_curve.axes = axes
        self.experimental_curve.plot_curve()
        # plot theoretical result curve
        x_coordinate = self.experimental_curve.src_coordinate.x
        y_coordinate = self.current_theoretical_y_coordinates
        axes.plot(x_coordinate,
                  y_coordinate,
                  lw=2,
                  label=self.current_label)

        y_coordinate = self.current_theoretical_y_coordinates_in_r_factor_region
        axes.fill_between(x_coordinate, x_coordinate * 0, y_coordinate,
                         alpha=0.2, edgecolor='#1B2ACC', facecolor='#089FFF',
                         linewidth=0.5, linestyle='dashdot', antialiased=True, label='$R_{factor}$ region')
        plt.title(self.current_txt)

    def save_current_curves_to_ascii_and_png_files(self):
        if self.out_directory_name is None:
            # time.sleep(5)
            self.out_directory_name = create_out_data_folder(
                main_folder_path=Configuration.PATH_TO_LOCAL_TMP_DIRECTORY,
                first_part_of_folder_name='multi-curves-fit-[{}]-[N={}]'.format(
                    str(self.experimental_curve.curve_label_latex).replace(' ', '_'),
                    self.number_of_curve_directory_paths_for_fit,
                ),
            )

        if self.experimental_curve.curve_label is None:
            self.experimental_curve.curve_label = 'Experiment'

        num_of_rows = len(self.experimental_curve.src_coordinate.x)

        out_array = np.zeros((num_of_rows, 5 + self.number_of_curve_directory_paths_for_fit))
        # Energy (eV):
        out_array[:, 0] = self.experimental_curve.src_coordinate.x
        # experimental curve:
        out_array[:, 1] = self.experimental_curve.src_coordinate.y
        # R-region of experimental curve:
        out_array[:, 2] = self.current_experimental_y_coordinates_in_r_factor_region
        # theory fit result:
        out_array[:, 3] = self.current_theoretical_y_coordinates
        # R-region of theory fit result:
        out_array[:, 4] = self.current_theoretical_y_coordinates_in_r_factor_region

        header_txt = 'R-factor region is [{}, {}]\n'.format(
            self.r_factor_region[0],
            self.r_factor_region[1],
        )
        header_txt = header_txt + 'minimization method: {}, number of fit models: {}\n'.format(
            self.minimization_method,
            self.number_of_curve_directory_paths_for_fit,
        )
        header_txt = header_txt + 'list of theoretical spectra directories from which models were taken:\n'
        for val in self.list_of_theoretical_spectra_directory_path:
            header_txt += '\t' + val + '\n'

        header_txt += self.current_txt + '\n\n'
        columns_name_txt = 'Energy(eV)\t{exper}\tR-region: [{exper}]\t{num} models fit\tR-region: [{num} models fit]'. \
            format(
            exper=self.experimental_curve.curve_label_latex,
            num=self.number_of_curve_directory_paths_for_fit,
        )
        for i, hs in enumerate(self.current_hash_list):
            current_curve = self.get_curve_by_hash(hs)
            # generate txt string:
            columns_name_txt += '\t{}'.format(
                current_curve.curve_label_latex,
            )
            # theory model y coordinate:
            out_array[:, 5 + i] = current_curve.src_coordinate.y
        header_txt += columns_name_txt

        self.current_out_directory_name = create_out_data_folder(
            main_folder_path=self.out_directory_name,
            first_part_of_folder_name='out',
        )
        self.current_out_file_name = 'R={} [{}] fit by N={} models'.format(
            round(self.current_r_factor, 5),
            self.experimental_curve.curve_label_latex,
            self.number_of_curve_directory_paths_for_fit,
        ).replace(' ', '_')
        np.savetxt(os.path.join(self.current_out_directory_name,
                                self.current_out_file_name + '.txt'),
                   out_array, fmt='%1.6e',
                   delimiter='\t', header=header_txt)

        # save to the PNG file:
        plt.draw()
        plt.show()
        self.figure.savefig(os.path.join(self.current_out_directory_name,
                                self.current_out_file_name + '.png'),
                            dpi=Configuration.DPI,
                            format='png',
                            # bbox_inches='tight', pad_inches=0.5,
                            )
        logger.info(os.path.join(self.current_out_directory_name,
                                self.current_out_file_name + '.png'))


if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')
    obj = MultiCurve()
    obj.list_of_theoretical_spectra_directory_path = [
        '/home/yugin/PycharmProjects/feff_find_best_fit/data/tmp_theoretical/Ira/',
        '/home/yugin/PycharmProjects/feff_find_best_fit/data/tmp_theoretical/Ira/',
        '/home/yugin/PycharmProjects/feff_find_best_fit/data/tmp_theoretical/Ira/',
        '/home/yugin/PycharmProjects/feff_find_best_fit/data/tmp_theoretical/Ira/',
    ]
    obj.list_of_cut_parts_of_file_name = [
        'Ira',
        'Ira',
        'Ira',
        'Ira',
    ]
    obj.number_of_curve_directory_paths_for_fit = 4

    obj.setup_axes()
    obj.load_experimental_curve()
    obj.load_curves_to_dict_of_multi_curves_for_processing()

    obj.run_fit_procedure()
    logger.info('finish multicurve fit')

    plt.legend()
    plt.show(block=True)
    # plt.pause(3)
    print('stop')
