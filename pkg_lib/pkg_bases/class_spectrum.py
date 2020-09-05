'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 9/5/20
'''
import logging
import os
from pkg_lib.pkg_bases.class_base import BaseClass
import matplotlib.pyplot as plt
import numpy as np
import numba
from copy import deepcopy


@numba.jit('Tuple((f8[:], f8[:]))(f8[:], f8[:], f8[:])', cache=True)
def numba_select_points_in_region(x, y, r_factor_region):
    # select only the points (X,Y) in the region:
    indexMin = (np.abs(x - r_factor_region[0])).argmin()
    indexMax = (np.abs(x - r_factor_region[1])).argmin()
    out_x = np.zeros(len(x[indexMin:indexMax]))
    out_y = np.empty_like(out_x)
    out_x = x[indexMin:indexMax]
    out_y = y[indexMin:indexMax]
    return out_x, out_y


@numba.jit('f8(f8[:], f8[:])', cache=True)
def get_R_factor_numba(y_ideal, y_probe):
    # calc R-factor
    # y_ideal - ideal curve
    # y_probe - probing curve
    A1 = np.power(np.abs(np.subtract(y_ideal, y_probe)), 2)
    A2 = np.power(np.abs(y_ideal), 2)
    return (np.sum(A1) / np.sum(A2))


@numba.jit('f8(f8[:], f8[:])', cache=True)
def get_R_factor_numba_v(y_ideal, y_probe):
    # calc R-factor
    # y_ideal - ideal curve
    # y_probe - probing curve
    N = y_ideal.size
    A1 = 0.0
    A2 = 0.0
    for i in range(N):
        A1 += (y_ideal[i]-y_probe[i])**2
        A2 += y_ideal[i]**2
    return A1/A2


def update_one_value_to_another_value(a, b):
    if a is not None and b is None:
        b = deepcopy(a)
    if b is not None and a is None:
       a = deepcopy(b)

    return a, b


class DecartXY(BaseClass):
    def __init__(self):
        self.x = None
        self.y = None


class Curve(BaseClass):
    def __init__(self):
        self.coordinate = DecartXY()
        self.plot_region = DecartXY()
        self.label = DecartXY()
        self.label_latex = DecartXY()
        self.curve_label = None
        self.curve_label_latex = None

    def update_label(self):
        if self.label.x is None:
            self.label.x = 'X'
        if self.label.y is None:
            self.label.y = 'Y'

        self.curve_label, self.curve_label_latex = \
            update_one_value_to_another_value(self.curve_label, self.curve_label_latex)

        if self.curve_label is None:
            self.curve_label = 'Curve Y vs X'
            self.curve_label, self.curve_label_latex = \
                update_one_value_to_another_value(self.curve_label, self.curve_label_latex)


    def plot_curve(self):
        self.update_label()
        plt.plot(self.coordinate.x,
                 self.coordinate.y,
                 lw=2,
                 label=self.curve_label_latex)
        plt.ylabel(self.label.y, fontsize=20, fontweight='bold')
        plt.xlabel(self.label.x, fontsize=20, fontweight='bold')


class TwoCurvesSpectrum(BaseClass):
    def __init__(self):
        self.ideal_curve = Curve()
        self.probe_curve = Curve()





if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')
    obj = Curve()
    obj.coordinate.x = np.r_[0:20.05:0.05]
    obj.coordinate.y = np.sin(obj.coordinate.x)
    obj.plot_curve()
    plt.show()
