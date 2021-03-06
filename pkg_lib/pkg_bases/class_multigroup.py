'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 01.02.2021
'''

from pkg_lib.pkg_bases.class_multicurve import *
from pkg_lib.pkg_cfg.class_configure import Configuration


class MultiGroupCurve(ExtendBase):
    '''
        Class to fit experimental model by using several angles and several theoretical models.
        The experiment consists of data for several angles.
        We have to determine the number of models for linear fit, and furthermore, we need to divide the data for each
        theoretical spectrum by angles. As a result, we calculate the R-factor by the number of angles of the
        experimental spectra, which will be fitted using the linear composition of the selected number of
        theoretical models.
    '''
    def __init__(self):
        super(MultiGroupCurve, self).__init__()
        # The name of sample type which will be used in output filename:
        self.sample_type_name = 'ZnO-ref'
        self.list_of_theoretical_spectra_directory_path = []
        # the word by which the full path to the file will be cut and the curve name will be created
        self.list_of_cut_parts_of_file_name = []
        # the linker between tha groups name and the sub-folder names
        # ex: group_name_and_mask_dict: {1: {'name': '45 deg', 'mask': 'aver'},}:
        self.group_name_and_mask_linker_dict = None

        self.number_of_curve_directory_paths_for_fit = None

        self.current_multi_curve = SubMultiCurve()
        self.r_factor_region = Configuration.SPECTRUM_CALCULATION_R_FACTOR_REGION

        # set limits for create interpolation energy (x- coordinates) for loaded spectra
        #  do not use:
        self.max_of_minimum_energy_point = -1e6
        self.min_of_maximum_energy_point = 1e6
        self.number_of_energy_points = 100

        # the dict of the self.number_of_curves_for_fit of curves for optimizing:
        self.dict_of_multi_curves_for_processing = None
        self.dict_of_hash_and_dict_of_group_curves_combinations_for_processing = None

        self.dict_of_experimental_curves_separated_by_groups = None

        self.list_of_hash_combinations = None
        self.minimization_method = 'differential_evolution'
        # self.minimization_method = 'minimize'
        # variables for processing for each step of calculations:
        self.current_hash_list = None
        self.current_group_id = None
        self.current_group_name = None

        self.current_dict_of_result_of_theoretical_y_coordinates = odict()
        self.current_dict_of_experimental_y_coordinates_in_r_factor_region = odict()
        self.current_dict_of_result_of_theoretical_y_coordinates_in_r_factor_region = odict()

        self.current_theoretical_y_coordinates = None
        self.current_experimental_y_coordinates_in_r_factor_region = None
        self.current_theoretical_y_coordinates_in_r_factor_region = None

        self.current_r_factor_dict = None
        self.current_sigma_squared_dict = None
        self.current_optimized_params = None
        self.current_title_txt = None
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
        self.group_name_and_mask_linker_dict = None
        self.number_of_curve_directory_paths_for_fit = None
        self.current_multi_curve = SubMultiCurve()
        self.max_of_minimum_energy_point = -1e6
        self.min_of_maximum_energy_point = 1e6
        self.number_of_energy_points = 100
        self.dict_of_multi_curves_for_processing = None
        self.dict_of_hash_and_dict_of_group_curves_combinations_for_processing = None
        self.dict_of_experimental_curves_separated_by_groups = None
        self.dict_of_results = None
        self.result_average_y = None
        self.optimized_params = []
        self.out_directory_name = None

        self.current_hash_list = None
        self.current_group_id = None
        self.current_group_name = None
        self.current_dict_of_result_of_theoretical_y_coordinates = odict()
        self.current_dict_of_experimental_y_coordinates_in_r_factor_region = odict()
        self.current_dict_of_result_of_theoretical_y_coordinates_in_r_factor_region = odict()

        self.current_theoretical_y_coordinates = None
        self.current_experimental_y_coordinates_in_r_factor_region = None
        self.current_theoretical_y_coordinates_in_r_factor_region = None
        self.current_r_factor_dict = None
        self.current_sigma_squared_dict = None

        self.current_optimized_params = None
        self.current_txt = None
        self.current_label = None
        self.current_out_directory_name = None
        self.current_out_file_name = None
        self.global_minimum_r_factor = 10
        self.dict_of_results = odict()
        self.out_directory_name = None

    def setup_axes(self):
        plt.ion()  # Force interactive
        plt.close('all')
        plt.switch_backend('QT5Agg', )
        plt.rc('font', family='serif')
        self.figure = plt.figure(figsize=(np.array(Configuration.FIGURE_GEOMETRY[2:]))/Configuration.DPI)
        self.figure_manager = plt.get_current_fig_manager()
        gspec = gridspec.GridSpec(
            nrows=2, ncols=len(self.group_name_and_mask_linker_dict), figure=self.figure)

        self.axes = list()
        # # add main subplot axes for fit result:
        # self.axes.append(self.figure.add_subplot(gspec[:, 0]))
        # add subplots for each sub-multicurve:
        for row in range(2):
            for col in range(len(self.group_name_and_mask_linker_dict)):
                self.axes.append(self.figure.add_subplot(gspec[row, col]))

        for val in self.axes:
            for axis in ['top', 'bottom', 'left', 'right']:
                val.spines[axis].set_linewidth(2)
        # for axis in ['top', 'bottom', 'left', 'right']:
        #     self.axes[0].spines[axis].set_linewidth(2)
        # plt.subplots_adjust(top=0.85)
        # gs1.tight_layout(fig, rect=[0, 0.03, 1, 0.95])
        self.figure.tight_layout(rect=[0.01, 0.01, 1, 0.9], w_pad=1.5, h_pad=1.5)

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

    def clear_all_axes(self):
        for current_ax in self.axes:
            plt.axes(current_ax)
            plt.cla()

    def load_experimental_curve_to_dict(self):
        self.dict_of_experimental_curves_separated_by_groups = odict()
        for num, val in self.group_name_and_mask_linker_dict.items():
            self.load_experimental_curve(experiment_name_mask=val['experiment_name_mask'])
            self.get_points_for_experimental_curve_in_region()
            self.dict_of_experimental_curves_separated_by_groups[num] = {
                'experimental_curve': deepcopy(self.experimental_curve),
                'experimental_y_coordinates_in_r_factor_region':
                    deepcopy(self.current_experimental_y_coordinates_in_r_factor_region),
                'group_name': val["name"],
                'group_mask': val["mask"],
                'experiment_name_mask': val['experiment_name_mask'],
            }
            # pprint(self.dict_of_experimental_curves_separated_by_groups)
        return self.dict_of_experimental_curves_separated_by_groups

    def get_experimental_curve_by_group_id(self, id=None):
        out = None
        if id is not None:
            out = self.dict_of_experimental_curves_separated_by_groups[id]['experimental_curve']
        return out

    def get_experimental_curve_by_group_name(self, group_name=None):
        out = None
        if group_name is not None:
            for key, val in self.group_name_and_mask_linker_dict.items():
                if group_name in val['name']:
                    out = self.dict_of_experimental_curves_separated_by_groups[key]['experimental_curve']
                    return out
        return out

    def get_current_sub_multi_curve_by_id(self, idx=None):
        out = None
        if idx is not None:
            out = SubMultiCurve()
            # set the energy values and number of points:
            out.max_of_minimum_energy_point = self.max_of_minimum_energy_point
            out.min_of_maximum_energy_point = self.min_of_maximum_energy_point
            out.number_of_energy_points = self.number_of_energy_points

            # out.load_experimental_curve()

            # set the cut part name and directory path:
            out.cut_part_of_file_name = self.list_of_cut_parts_of_file_name[idx]
            out.working_directory_path = self.list_of_theoretical_spectra_directory_path[idx]

            # set group_name_and_mask_linker_dict value:
            out.group_name_and_mask_linker_dict = self.group_name_and_mask_linker_dict
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

            # prepare data from experimental curves:
            self.load_experimental_curve_to_dict()

            self.dict_of_multi_curves_for_processing = odict()
            for i in range(self.number_of_curve_directory_paths_for_fit):
                self.current_multi_curve = self.get_current_sub_multi_curve_by_id(idx=i)

                # put current multicurve into the dict:
                tmp_dict = odict()
                tmp_dict['id'] = i
                tmp_dict['curves'] = deepcopy(self.current_multi_curve)
                self.dict_of_multi_curves_for_processing[i] = tmp_dict

                self.current_multi_curve.axes = self.axes[1]
                self.current_multi_curve.plot_curves()
                self.current_multi_curve.axes.set_title(
                    self.list_of_cut_parts_of_file_name[i]
                )
                plt.legend()
                plt.draw()
                plt.show()

    def get_points_for_experimental_curve_in_region(self):
        '''
        make sure self.experimental_curve corresponds to the correct group of curves.
        :return:
        '''
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
        '''
        make sure self.experimental_curve and self.current_theoretical_y_coordinates correspond to the same
        group of curves. If not please re-initialize these values.
        :return:
        '''
        x_vector = self.experimental_curve.src_coordinate.x
        y_vector = copy(self.current_theoretical_y_coordinates)

        out_x, out_y, y_in_r_region, index_min, index_max = get_points_and_indices_in_region(
            x_vector=x_vector,
            y_vector=y_vector,
            r_factor_region=self.r_factor_region,
        )
        self.current_theoretical_y_coordinates_in_r_factor_region = y_in_r_region
        return out_x, out_y, y_in_r_region, index_min, index_max

    def get_r_factor_from_current_vectors(self):
        y_ideal = self.current_experimental_y_coordinates_in_r_factor_region
        # update values of theoretical data:
        self.get_points_for_current_theoretical_curve_in_region()
        y_probe = self.current_theoretical_y_coordinates_in_r_factor_region
        if (y_ideal is not None) and (y_probe is not None):
            self.current_r_factor_dict = get_r_factor_numba_v(np.asarray(y_ideal, dtype=float),
                                                              np.asarray(y_probe, dtype=float))
            return self.current_r_factor_dict
        else:
            return None

    def get_r_factor_and_sigma_squared_from_dict_of_y_coordinates_in_r_factor_region(self):
        self.current_r_factor_dict = odict()
        self.current_sigma_squared_dict = odict()
        r_factor = 0
        total_r_factor = 0
        s2 = 0
        total_s2 = 0
        for group_key, group_val in self.current_dict_of_result_of_theoretical_y_coordinates_in_r_factor_region.items():
            y_ideal = \
                self.dict_of_experimental_curves_separated_by_groups[group_key]['experimental_y_coordinates_in_r_factor_region']
            y_probe = group_val
            if (y_ideal is not None) and (y_probe is not None):
                r_factor = get_r_factor_numba_v(np.asarray(y_ideal, dtype=float),
                                                                   np.asarray(y_probe, dtype=float))
                self.current_r_factor_dict[group_key] = r_factor
                total_r_factor += r_factor

                s2 = np.sum((y_ideal - y_probe) ** 2) / (len(y_ideal) - 1)
                self.current_sigma_squared_dict[group_key] = s2
                total_s2 += s2
        # store total values:
        self.current_r_factor_dict['total'] = total_r_factor
        self.current_sigma_squared_dict['total'] = total_s2

        return self.current_r_factor_dict, self.current_sigma_squared_dict

    def get_sigma_squared_from_current_vectors(self):
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
        self.current_sigma_squared_dict = s2
        return s2

    def get_dict_of_hash_and_dict_of_group_curves_combinations_for_processing(self):
        '''
        create dict of hash - curves
        :return: dict of hash [which corresponds to unique model path name] <-> dict of (group of curves)
        ('84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
              {1: {'group_id': 1,
                   'group_name': '0 deg',
                   'model_name': '|ZnO+Ovac|',
                   'name': '0 deg',
                   'theoretical_curve': <pkg_lib.pkg_bases.class_spectrum.Curve object at 0x7fd2c0589580>},
               2: {'group_id': 2,
                   'group_name': '45 deg',
                   'model_name': '|ZnO+Ovac|',
                   'name': '45 deg',
                   'theoretical_curve': <pkg_lib.pkg_bases.class_spectrum.Curve object at 0x7fd2c05893d0>},
               3: {'group_id': 3,
                   'group_name': '75 deg',
                   'model_name': '|ZnO+Ovac|',
                   'name': '75 deg',
                   'theoretical_curve': <pkg_lib.pkg_bases.class_spectrum.Curve object at 0x7fd2c0589520>}}),
        '''
        self.dict_of_hash_and_dict_of_group_curves_combinations_for_processing = odict()
        for key, val in self.dict_of_multi_curves_for_processing.items():
            for key_in, val_in in val['curves'].dict_of_theoretical_curves.items():
                tmp_dict = {}

                try:
                    for key_inside, val_inside in val['curves'].dict_of_theoretical_curves.items():
                        if val_in['hash'] in val_inside['hash']:
                            # befor use self.get_points_for_current_theoretical_curve_in_region we re-initialize needed
                            # values:
                            self.experimental_curve = self.get_experimental_curve_by_group_id(id=val_inside['group_id'])
                            self.current_theoretical_y_coordinates = val_inside['curve'].src_coordinate.y
                            self.get_points_for_current_theoretical_curve_in_region()
                            tmp_dict[val_inside['group_id']] = {
                                'theoretical_curve': val_inside['curve'],
                                'theoretical_y_coordinates_in_r_factor_region':
                                    deepcopy(self.current_theoretical_y_coordinates_in_r_factor_region),
                                'group_id': val_inside['group_id'],
                                'group_name': val_inside['group_name'],
                                'name': val_inside['name'],
                                'filename': val_inside['filename'],
                                'model_name': val_inside['model_name'],
                                'model_path': val_inside['model_path'],
                            }
                    self.dict_of_hash_and_dict_of_group_curves_combinations_for_processing[val_in['hash']] = tmp_dict
                except Exception as err:
                    logger.error(err)
                    logger.exception(err)
                    # logger.error(f'key:{key_in} val:{val_in}')
        return self.dict_of_hash_and_dict_of_group_curves_combinations_for_processing

    def get_dict_of_groups_of_curves_by_hash(self, hash=None):
        '''

        :param hash:
        :return: {
            1: {'group_id': 1,
               'group_name': '0 deg',
               'model_name': '|ZnO+Ovac|',
               'name': '0 deg',
               'theoretical_curve': <pkg_lib.pkg_bases.class_spectrum.Curve object at 0x7fd2c0589580>},
               'theoretical_y_coordinates_in_r_factor_region':....
            2: {'group_id': 2,
               'group_name': '45 deg',
               'model_name': '|ZnO+Ovac|',
               'name': '45 deg',
               'theoretical_curve': <pkg_lib.pkg_bases.class_spectrum.Curve object at 0x7fd2c05893d0>},
               'theoretical_y_coordinates_in_r_factor_region':....
            3: {'group_id': 3,
               'group_name': '75 deg',
               'model_name': '|ZnO+Ovac|',
               'name': '75 deg',
               'theoretical_curve': <pkg_lib.pkg_bases.class_spectrum.Curve object at 0x7fd2c0589520>},
               'theoretical_y_coordinates_in_r_factor_region':....
               }
        '''
        out = None
        try:
            out = self.dict_of_hash_and_dict_of_group_curves_combinations_for_processing[hash]
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
        result_hash_list_combinations_without_duplicates.sort()
        self.list_of_hash_combinations = result_hash_list_combinations_without_duplicates
        # pprint(self.list_of_hash_combinations)
        return result_hash_list_combinations_without_duplicates

    def func_for_optimize(self, x):
        # create function of snapshots linear composition Sum[x_i*F_i]
        num = len(self.group_name_and_mask_linker_dict)
        x = np.abs(x)
        tmp_y_vector = []
        sum_x = np.sum(x)
        tmp_dict_of_theoretical_y_coordinates_src = odict()
        tmp_dict_of_theoretical_y_coordinates_in_r_factor_region = odict()
        coordinate_y_in_r_region = None
        for i, hash in enumerate(self.current_hash_list):
            if abs(sum_x) > 0:
                k = x[i] / sum_x
            else:
                k = x[i]

            for group_key, group_val in self.get_dict_of_groups_of_curves_by_hash(hash=hash).items():

                coordinate_y_in_r_region = group_val['theoretical_y_coordinates_in_r_factor_region']
                coordinate_y_src = group_val['theoretical_curve'].src_coordinate.y
                if i < 1:
                    tmp_dict_of_theoretical_y_coordinates_in_r_factor_region[group_key] = k * coordinate_y_in_r_region

                    tmp_dict_of_theoretical_y_coordinates_src[group_key] = k * coordinate_y_src
                    # tmp_y_vector = k * self.get_dict_group_of_curves_by_hash(hash=hash).src_coordinate.y

                else:
                    tmp_dict_of_theoretical_y_coordinates_in_r_factor_region[group_key] += k * coordinate_y_in_r_region

                    tmp_dict_of_theoretical_y_coordinates_src[group_key] += k * coordinate_y_src

        return tmp_dict_of_theoretical_y_coordinates_in_r_factor_region, tmp_dict_of_theoretical_y_coordinates_src

    def run_fit_procedure_for_current_values(self):
        num = self.number_of_curve_directory_paths_for_fit
        x0 = np.zeros(num)
        # create bounds:
        bounds = []
        for i in x0:
            bounds.append((0, 1))

        def func(x):
            a, b = self.func_for_optimize(x)
            self.current_dict_of_result_of_theoretical_y_coordinates_in_r_factor_region = a
            self.current_dict_of_result_of_theoretical_y_coordinates = b
            self.get_r_factor_and_sigma_squared_from_dict_of_y_coordinates_in_r_factor_region()
            return self.current_r_factor_dict['total']

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
        self.dict_of_results = odict()
        # generate list of tuples of hashes:
        self.get_hash_list_of_curves_combinations()
        # generate special form of dict for quick data access by hash:
        self.get_dict_of_hash_and_dict_of_group_curves_combinations_for_processing()
        # # prepare data from experimental curve:
        # self.get_points_for_experimental_curve_in_region()
        for num, val_lst in enumerate(self.list_of_hash_combinations):
            self.current_hash_list = val_lst
            self.run_fit_procedure_for_current_values()
            if self.is_global_minimum_r_factor():
                tmp_dict = odict()
                tmp_dict['r_factor'] = deepcopy(self.current_r_factor_dict)
                tmp_dict['sigma_squared'] = deepcopy(self.current_sigma_squared_dict)
                tmp_dict['hash_list'] = deepcopy(self.current_hash_list)
                tmp_dict['optimized_params'] = deepcopy(self.current_optimized_params)
                tmp_dict['x_coordinates'] = deepcopy(self.experimental_curve.src_coordinate.x)
                tmp_dict['theoretical_y_coordinates'] = deepcopy(self.current_dict_of_result_of_theoretical_y_coordinates)
                tmp_dict['theoretical_y_coordinates_in_r_factor_region'] = \
                    deepcopy(self.current_dict_of_result_of_theoretical_y_coordinates_in_r_factor_region)

                self.dict_of_results[num] = tmp_dict

                # write Title:
                self.current_title_txt = 'Total values: $\\mathbf{{R}}$={rf:1.7f}, $\\mathbf{{' \
                                         '\sigma^2}}$={sq:1.7f}\n'.format(
                    rf=self.current_r_factor_dict['total'],
                    sq=self.current_sigma_squared_dict['total'],
                )
                self.figure.suptitle(self.current_title_txt, fontsize=20)
                # plot curves
                self.clear_all_axes()
                for group_key, val in self.group_name_and_mask_linker_dict.items():
                    self.current_txt = '$\\mathbf{{{}}}$ : '.format(val['name'])
                    self.current_txt += 'R={rf:1.7f}, $\sigma^2$={sq:1.7f}\n'.format(
                        rf=self.current_r_factor_dict[group_key],
                        sq=self.current_sigma_squared_dict[group_key],
                    )
                    self.current_label = ''
                    self.experimental_curve = self.dict_of_experimental_curves_separated_by_groups[group_key][
                        'experimental_curve']
                    self.experimental_curve.axes = self.axes[group_key - 1 + len(self.group_name_and_mask_linker_dict)]
                    self.experimental_curve.plot_curve()
                    for i, hs in enumerate(self.current_hash_list):
                        current_dict_of_curve_group = self.get_dict_of_groups_of_curves_by_hash(hs)[group_key]
                        current_curve = current_dict_of_curve_group['theoretical_curve']
                        # generate txt string:
                        self.current_label = self.current_label + '{0} x [ '.format(
                            round(self.current_optimized_params[i], 5)
                        ) + current_dict_of_curve_group['name'] + ' ]'
                        if i < len(self.current_optimized_params) - 1:
                            self.current_label = self.current_label + ' + \n'
                        current_curve.axes = self.axes[group_key - 1 + len(self.group_name_and_mask_linker_dict)]
                        plt.axes(current_curve.axes)
                        # init experimental curve for current group:
                        current_curve.plot_curve()
                        # self.experimental_curve.is_src_plotted = True
                        plt.legend()
                        plt.grid(True)
                        plt.draw()
                        plt.show()
                    self.plot_fit_resulted_for_current_group_of_curves(group_id=group_key)
                    plt.legend()
                    plt.draw()
                    plt.show()

                # self.current_txt = self.current_txt + self.current_label
                self.save_current_curves_to_ascii_and_png_files()
        # copy the global minimum files into up directory:
        if self.current_out_file_name is not None:
            source = self.current_out_directory_name
            destination = self.out_directory_name
            shutil.copytree(source, destination, dirs_exist_ok=True)

    def is_global_minimum_r_factor(self):
        if self.current_r_factor_dict['total'] <= self.global_minimum_r_factor:
            self.global_minimum_r_factor = copy(self.current_r_factor_dict['total'])
            return True
        else:
            return False

    def plot_fit_resulted_for_current_group_of_curves(self, group_id=None):
        if group_id is not None:
            axes = self.axes[group_id - 1]
            plt.axes(axes)
            plt.cla()
            # before starting this procedure, it is necessary to initialize the experimental curve.
            self.experimental_curve.axes = axes
            self.experimental_curve.plot_curve()
            # plot theoretical result curve
            x_coordinate = self.experimental_curve.src_coordinate.x
            y_coordinate = self.current_dict_of_result_of_theoretical_y_coordinates[group_id]
            axes.plot(x_coordinate,
                      y_coordinate,
                      lw=2,
                      label=self.current_label)

            y_coordinate = self.current_dict_of_result_of_theoretical_y_coordinates_in_r_factor_region[group_id]
            axes.fill_between(x_coordinate, x_coordinate * 0, y_coordinate,
                             alpha=0.2, edgecolor='#1B2ACC', facecolor='#089FFF',
                             linewidth=0.5, linestyle='dashdot', antialiased=True, label='$R_{factor}$ region')
            plt.title(self.current_txt)
            plt.grid(True)

    def save_current_curves_to_ascii_and_png_files(self):
        if self.out_directory_name is None:
            # time.sleep(5)
            self.out_directory_name = create_out_data_folder(
                main_folder_path=Configuration.PATH_TO_LOCAL_TMP_DIRECTORY,
                first_part_of_folder_name='multi-curves-fit-[{}]-[G={}]-[M={}]'.format(
                    self.sample_type_name,
                    len(self.group_name_and_mask_linker_dict),
                    self.number_of_curve_directory_paths_for_fit,
                ),
            )
        self.current_out_directory_name = create_out_data_folder(
            main_folder_path=self.out_directory_name,
            first_part_of_folder_name='out',
        )
        for group_key, group_val in self.group_name_and_mask_linker_dict.items():
            self.experimental_curve = self.get_experimental_curve_by_group_id(group_key)
            header_txt = 'Total values: R(tot)={rf:1.7f}, Sigma^2(tot)={sq:1.7f}\n'.format(
                rf=self.current_r_factor_dict['total'],
                sq=self.current_sigma_squared_dict['total'],
            )
            header_txt += '{} : '.format(group_val['name'])
            header_txt += 'R={rf:1.7f}, sigma^2={sq:1.7f}\n'.format(
                rf=self.current_r_factor_dict[group_key],
                sq=self.current_sigma_squared_dict[group_key],
            )
            num_of_rows = len(self.get_experimental_curve_by_group_id(group_key).src_coordinate.x)
            out_array = np.zeros((num_of_rows, 5 + self.number_of_curve_directory_paths_for_fit))
            # Energy (eV):
            out_array[:, 0] = self.experimental_curve.src_coordinate.x
            # experimental curve:
            out_array[:, 1] = self.experimental_curve.src_coordinate.y
            # R-region of experimental curve:
            out_array[:, 2] = \
                self.dict_of_experimental_curves_separated_by_groups[group_key][
                    'experimental_y_coordinates_in_r_factor_region']
            # theory fit result:
            out_array[:, 3] = self.current_dict_of_result_of_theoretical_y_coordinates[group_key]
            # R-region of theory fit result:
            out_array[:, 4] = self.current_dict_of_result_of_theoretical_y_coordinates_in_r_factor_region[group_key]

            header_txt += 'R-factor region is [{}, {}]\n'.format(
                self.r_factor_region[0],
                self.r_factor_region[1],
            )
            header_txt = header_txt + 'minimization method: {}, number of fit models: {}, number of groups: {}\n'.format(
                self.minimization_method,
                self.number_of_curve_directory_paths_for_fit,
                len(self.group_name_and_mask_linker_dict),
            )
            header_txt = header_txt + 'list of theoretical spectra directories from which models were taken:\n'
            for val in self.list_of_theoretical_spectra_directory_path:
                header_txt += '\t' + val + '\n'

            columns_name_txt = 'Energy(eV)\tRaw:[{exper}]\tRaw R-region: [{exper}]\tTotal:[{exper}] [{num} models ' \
                               'fit]\tTotal:[{exper}] R-region: [{num} models fit]'.format(
                exper=group_val['name'],
                num=self.number_of_curve_directory_paths_for_fit,
            )

            current_label = ''
            for i, hs in enumerate(self.current_hash_list):
                current_dict_of_curve_group = self.get_dict_of_groups_of_curves_by_hash(hs)[group_key]
                current_curve = current_dict_of_curve_group['theoretical_curve']
                # generate txt string:
                current_label = current_label + '{0} x [ '.format(
                    round(self.current_optimized_params[i], 5)
                ) + current_dict_of_curve_group['name'] + ' ]'
                if i < len(self.current_optimized_params) - 1:
                    current_label = current_label + ' + \n'
                # generate txt string:
                columns_name_txt += '\t{}'.format(
                    current_dict_of_curve_group['name'],
                )
                # theory model y coordinate:
                out_array[:, 5 + i] = current_curve.src_coordinate.y
            header_txt += current_label
            header_txt += '\n\n'
            header_txt += columns_name_txt

            self.current_out_file_name = 'R={} [{}] Group name [{}] fit by M={} models and G={} groups'.format(
                round(self.current_r_factor_dict['total'], 5),
                self.sample_type_name,
                group_val['name'],
                self.number_of_curve_directory_paths_for_fit,
                len(self.group_name_and_mask_linker_dict),
            ).replace(' ', '_')
            np.savetxt(os.path.join(self.current_out_directory_name,
                                    self.current_out_file_name + '.txt'),
                       out_array, fmt='%1.6e',
                       delimiter='\t', header=header_txt)

        # save to the PNG file:
        plt.draw()
        plt.show()
        self.current_out_file_name = 'R={} [{}] fit by M={} models and G={} groups'.format(
            round(self.current_r_factor_dict['total'], 5),
            self.sample_type_name,
            self.number_of_curve_directory_paths_for_fit,
            len(self.group_name_and_mask_linker_dict),
        ).replace(' ', '_')
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
    sample_type = 'ZnO_ref'
    sample_type = 'YbZnO_5e14'
    sample_type = 'YbZnO_5e15'

    obj = MultiGroupCurve()
    obj.sample_type_name = sample_type
    obj.list_of_theoretical_spectra_directory_path = [
        '/home/yugin/PycharmProjects/feff_find_best_fit/data/tmp_theoretical/Ira/',
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
        'Ira',
    ]

    if sample_type == 'ZnO_ref':
        Configuration.EXPERIMENTAL_SPECTRA_FILE_NAME = 'experiment_ZnO_O-Kedge_[0,45,75].dat'
        Configuration.EXPERIMENTAL_SPECTRUM_X_SHIFT = -541.99
        Configuration.EXPERIMENTAL_SPECTRUM_Y_SHIFT = -1.865
        Configuration.EXPERIMENTAL_SPECTRUM_Y_SCALE = 0.853

        Configuration.EXPERIMENTAL_SPECTRA_FILE_NAME = 'experiment_ZnO__ref_O-Kedge_[0,45,75].dat'
        Configuration.EXPERIMENTAL_SPECTRUM_Y_SHIFT = 0
        Configuration.EXPERIMENTAL_SPECTRUM_Y_SCALE = 1
        # /home/yugin/PycharmProjects/feff_find_best_fit/data/tmp_theoretical/Ira/ZnO+Ovac/0.2679 0 1/
        # group key must start at 1 and increase by 1.
        obj.group_name_and_mask_linker_dict = {
            1: {'name': '0 deg', 'mask': '100', 'experiment_name_mask': 'ZnO-0deg'},
            2: {'name': '45 deg', 'mask': 'aver', 'experiment_name_mask': 'ZnO-45deg'},
            3: {'name': '75 deg', 'mask': '0.2679 0 1', 'experiment_name_mask': 'ZnO-75deg'},
        }

        # obj.group_name_and_mask_linker_dict = {
        #     1: {'name': '45 deg', 'mask': 'aver', 'experiment_name_mask': 'ZnO-45deg'},
        #     2: {'name': '75 deg', 'mask': '0.2679 0 1', 'experiment_name_mask': 'ZnO-75deg'},
        # }

    if sample_type == 'YbZnO_5e14':
        obj.group_name_and_mask_linker_dict = {
            1: {'name': '0 deg', 'mask': '100', 'experiment_name_mask': 'YbZnO_5e14-0deg'},
            2: {'name': '45 deg', 'mask': 'aver', 'experiment_name_mask': 'YbZnO_5e14-45deg'},
            3: {'name': '75 deg', 'mask': '0.2679 0 1', 'experiment_name_mask': 'YbZnO_5e14-75deg'},
        }
        Configuration.EXPERIMENTAL_SPECTRA_FILE_NAME = 'experiment_YbZnO__5e14_O-Kedge_[0,45,75].dat'
        Configuration.EXPERIMENTAL_SPECTRUM_X_SHIFT = -541.99
        Configuration.EXPERIMENTAL_SPECTRUM_Y_SHIFT = 0
        Configuration.EXPERIMENTAL_SPECTRUM_Y_SCALE = 1

    if sample_type == 'YbZnO_5e15':
        Configuration.EXPERIMENTAL_SPECTRA_FILE_NAME = 'experiment_YbZnO__5e15_O-Kedge_[0,45,75].dat'
        Configuration.EXPERIMENTAL_SPECTRUM_X_SHIFT = -541.99
        Configuration.EXPERIMENTAL_SPECTRUM_Y_SHIFT = 0
        Configuration.EXPERIMENTAL_SPECTRUM_Y_SCALE = 1
        obj.group_name_and_mask_linker_dict = {
            1: {'name': '0 deg', 'mask': '100', 'experiment_name_mask': 'YbZnO_5e15-0deg'},
            2: {'name': '45 deg', 'mask': 'aver', 'experiment_name_mask': 'YbZnO_5e15-45deg'},
            3: {'name': '75 deg', 'mask': '0.2679 0 1', 'experiment_name_mask': 'YbZnO_5e15-75deg'},
        }

    obj.number_of_curve_directory_paths_for_fit = 4
    Configuration.init()

    obj.setup_axes()
    obj.load_curves_to_dict_of_multi_curves_for_processing()

    obj.run_fit_procedure()
    logger.info('finish multicurve fit')

    plt.legend()
    plt.show(block=True)
    # plt.pause(3)
    print('stop')
