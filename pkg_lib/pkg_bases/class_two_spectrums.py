'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 15.09.2020
'''
from pkg_lib.pkg_bases.class_spectrum import *
from pkg_lib.pkg_bases.class_base import BaseClass
from collections import OrderedDict as odict
import numpy as np
from scipy.optimize import differential_evolution
import prettytable as pt


class DoubleCurves(BaseClass):
    def __init__(self):
        self.ideal_curve = Curve()
        self.probe_curve = Curve()
        self.ideal_curve_in_selected_region = Curve()
        self.probe_curve_in_selected_region = Curve()
        self.r_factor_region = Configuration.SPECTRUM_CALCULATION_R_FACTOR_REGION
        self.optimized_params = [0, 0, 0]

    def update_variables(self):
        self.probe_curve.transform_curve()
        self.ideal_curve.transform_curve()

        x1, y1 = self.select_points_in_region(self.ideal_curve.new_coordinate.x, self.ideal_curve.new_coordinate.y)
        x2, y2 = self.select_points_in_region(self.probe_curve.new_coordinate.x, self.probe_curve.new_coordinate.y)

        x_interp, y1_out, y2_out = self.interpolate_arrays_to_equal_length(x1, y1, x2, y2)

        self.ideal_curve_in_selected_region.src_coordinate.x = x_interp
        self.ideal_curve_in_selected_region.src_coordinate.y = y1_out

        self.probe_curve_in_selected_region.src_coordinate.x = x_interp
        self.probe_curve_in_selected_region.src_coordinate.y = y2_out

        self.probe_curve_in_selected_region.transform_curve()
        self.ideal_curve_in_selected_region.transform_curve()

    def plot_probe_curve(self, line_width=2, alpha=1.0, is_label=True):
        self.update_variables()
        vector_x = self.probe_curve.new_coordinate.x
        vector_y = self.probe_curve.new_coordinate.y
        lbl = self.probe_curve.curve_label_latex
        if is_label:
            plt.plot(vector_x, vector_y, lw=line_width, alpha=alpha, label=lbl)
        else:
            plt.plot(vector_x, vector_y, lw=line_width, alpha=alpha, label=None)
        plt.ylabel('$\mu(E)$', fontsize=20, fontweight='bold')
        plt.xlabel('$E$ $[eV]$', fontsize=20, fontweight='bold')

    def plot_two_curves(self):
        self.update_variables()
        probe_x = self.probe_curve.new_coordinate.x
        probe_y = self.probe_curve.new_coordinate.y
        lbl = self.probe_curve.curve_label_latex

        ideal_x = self.ideal_curve.new_coordinate.x
        ideal_y = self.ideal_curve.new_coordinate.y
        ideal_lbl = self.ideal_curve.curve_label_latex

        probe_in_region_x = self.probe_curve_in_selected_region.new_coordinate.x
        probe_in_region_y = self.probe_curve_in_selected_region.new_coordinate.y
        plt.plot(probe_x, probe_y, lw=2, label=lbl)
        plt.plot(ideal_x, ideal_y, lw=2, label=ideal_lbl)
        plt.fill_between(probe_in_region_x, probe_in_region_y * 0, probe_in_region_y,
                         alpha=0.2, edgecolor='#1B2ACC', facecolor='#089FFF',
                         linewidth=0.5, linestyle='dashdot', antialiased=True,
                         label='$R_{{factor}}$ region.\n$R_{{factor}}={r:0.4f}\%$ \n$S^2={s2:0.4f}\%$'.format(
                             r=self.get_r_factor()*100, s2=self.get_sigma_squared()*100))
        plt.ylabel('$\mu(E)$', fontsize=20, fontweight='bold')
        plt.xlabel('$E$ $[eV]$', fontsize=20, fontweight='bold')

    def select_points_in_region(self, x_vector=None, y_vector=None):
        # select only the points (X,Y) in the region:
        # indexMin = (np.abs(x - self.r_factor_region[0])).argmin()
        # indexMax = (np.abs(x - self.r_factor_region[1])).argmin()
        # out_x = x[indexMin:indexMax]
        # out_y = y[indexMin:indexMax]

        # replace by numba.jit
        out_x, out_y = numba_select_points_in_region(np.asarray(x_vector), np.asarray(y_vector), np.asarray(
            self.r_factor_region, dtype=float))

        return out_x, out_y

    @staticmethod
    def interpolate_arrays_to_equal_length(x1, y1, x2, y2):
        # x1,y1 - first array of x,y values
        # x2,y2 - second array of x,y values

        l1 = len(x1)
        l2 = len(x2)
        if l1 >= l2:
            num = l1
            x_interp = x1
        else:
            num = l2
            x_interp = x2

        y1_out = np.interp(x_interp, x1, y1)
        y2_out = np.interp(x_interp, x2, y2)

        # return the same length 3-arrays
        return x_interp, y1_out, y2_out

    def get_r_factor(self):
        # calc R-factor
        # y_ideal - ideal curve
        # y_probe - probing curve

        # A1 = np.power(np.abs(np.subtract(y_ideal - y_probe)), 2)
        # A2 = np.power(np.abs(y_ideal), 2)
        # return (np.sum(A1) / np.sum(A2))
        y_ideal = self.ideal_curve_in_selected_region.new_coordinate.y
        y_probe = self.probe_curve_in_selected_region.new_coordinate.y
        # replace by numba:
        if (y_ideal is not None) and (y_probe is not None):
            return get_r_factor_numba_v(np.asarray(y_ideal, dtype=float), np.asarray(y_probe, dtype=float))
        else:
            return None

    def get_sigma_squared(self):
        '''
        return unbiased sample variance of vector
        :return:
        '''
        s2 = None
        y_ideal = self.ideal_curve_in_selected_region.new_coordinate.y
        y_probe = self.probe_curve_in_selected_region.new_coordinate.y
        # replace by numba:
        if (y_ideal is not None) and (y_probe is not None):
            s2 = np.sum((y_ideal - y_probe) ** 2) / (len(y_ideal) - 1)
        return s2

    def func_for_optimize(self, params_vector):
        # create function of minimization: params_vector
        self.probe_curve.transform_coefficient.scale_factor.y = params_vector[0]

        self.probe_curve.transform_coefficient.shift_factor.x = params_vector[1]
        self.probe_curve.transform_coefficient.shift_factor.y = params_vector[2]

    def optimize_probe_curve_params(self):
        # optimize probe_curve.transform_coefficient to find better fit ideal_curve
        def func(params_vector):
            self.func_for_optimize(params_vector)
            self.update_variables()
            return self.get_r_factor()

        # create bounds:
        bounds = [
            (0, 2),  # scale_factor.y
            (-1, 2),  # shift_factor.x
            (-1, 2),  # shift_factor.y
                  ]

        res = differential_evolution(func, bounds)
        self.optimized_params = res.x

    def show_optimum(self):
        table = pt.PrettyTable([
            'R-factor',
            'S2',
            'Y-scale',
            'X-shift',
            'Y-shift',
        ])
        table.add_row(
            [
                '{:0.6f}'.format(self.get_r_factor()),
                '{:0.6f}'.format(self.get_sigma_squared()),
                '{:0.6f}'.format(self.optimized_params[0]),
                '{:0.6f}'.format(self.optimized_params[1]),
                '{:0.6f}'.format(self.optimized_params[2]),
            ]
        )
        print(table)


if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')
    obj_2d = DoubleCurves()

    obj = Curve()
    file_path1 = os.path.join(
        Configuration.PATH_TO_LOCAL_DATA_DIRECTORY, 'tmp_theoretical', 'ZnO_ideal_p=[100]_0001', 'xmu.dat')

    obj.src_coordinate.x, obj.src_coordinate.y = load_theoretical_xmu_data(file_path1)
    # obj.curve_label = 'ZnO_ideal_p=[100]'
    # obj.plot_curve()

    data = load_experimental_data()

    obj_2d.ideal_curve.src_coordinate.x = data[:, 0]
    obj_2d.ideal_curve.src_coordinate.y = data[:, 1]
    obj_2d.ideal_curve.curve_label_latex = 'ZnO-0deg'

    obj_2d.probe_curve.src_coordinate.x = obj.src_coordinate.x
    obj_2d.probe_curve.src_coordinate.y = obj.src_coordinate.y
    obj_2d.probe_curve.transform_coefficient.shift_factor.y = -0.05
    obj_2d.probe_curve.curve_label_latex = 'ZnO_ideal_p=[100]'

    obj_2d.update_variables()
    obj_2d.plot_two_curves()
    obj_2d.show_optimum()

    obj_2d.optimize_probe_curve_params()

    obj_2d.show_optimum()
    obj_2d.probe_curve.curve_label_latex = 'opt:ZnO_ideal_p=[100]'
    obj_2d.plot_two_curves()
    plt.legend()
    plt.show()



