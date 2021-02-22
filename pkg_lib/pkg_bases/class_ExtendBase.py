'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 11.01.2021
'''
from pkg_lib.pkg_bases.class_spectrum import *
import matplotlib.gridspec as gridspec


class ExtendBase(BaseClass):
    def __init__(self):
        super(ExtendBase, self).__init__()
        self.experimental_curve = Curve()

        self.axes = None
        self.figure = None
        self.figure_manager = None

    def load_experimental_curve(self, experiment_name_mask=None):
        data = load_experimental_data()
        if experiment_name_mask is None:
            experiment_name_mask = 'ZnO-0deg'
        if experiment_name_mask in 'ZnO-0deg':
            self.experimental_curve.src_coordinate.x = data[:, 0]
            self.experimental_curve.src_coordinate.y = data[:, 1]
            self.experimental_curve.curve_label_latex = 'ZnO-0deg'
            self.experimental_curve.label.x = 'Energy,[eV]'
            self.experimental_curve.label.y = 'Intensity,[a.u.]'
            # self.experimental_curve.plot_curve()
            # plt.draw()

        if experiment_name_mask in 'ZnO-45deg':
            self.experimental_curve.src_coordinate.x = data[:, 0]
            self.experimental_curve.src_coordinate.y = data[:, 2]
            self.experimental_curve.curve_label_latex = 'ZnO-45deg'
            self.experimental_curve.label.x = 'Energy,[eV]'
            self.experimental_curve.label.y = 'Intensity,[a.u.]'
            # self.experimental_curve.plot_curve()
            # plt.draw()

        if experiment_name_mask in 'ZnO-75deg':
            self.experimental_curve.src_coordinate.x = data[:, 0]
            self.experimental_curve.src_coordinate.y = data[:, 3]
            self.experimental_curve.curve_label_latex = 'ZnO-75deg'
            self.experimental_curve.label.x = 'Energy,[eV]'
            self.experimental_curve.label.y = 'Intensity,[a.u.]'
            # self.experimental_curve.plot_curve()
            # plt.draw()

        #     -------------------- YbZnO_5e14
        if experiment_name_mask in 'YbZnO_5e14-0deg':
            self.experimental_curve.src_coordinate.x = data[:, 0]
            self.experimental_curve.src_coordinate.y = data[:, 1]
            self.experimental_curve.curve_label_latex = 'YbZnO_5e14-0deg'
            self.experimental_curve.label.x = 'Energy,[eV]'
            self.experimental_curve.label.y = 'Intensity,[a.u.]'
            # self.experimental_curve.plot_curve()
            # plt.draw()

        if experiment_name_mask in 'YbZnO_5e14-45deg':
            self.experimental_curve.src_coordinate.x = data[:, 0]
            self.experimental_curve.src_coordinate.y = data[:, 2]
            self.experimental_curve.curve_label_latex = 'YbZnO_5e14-45deg'
            self.experimental_curve.label.x = 'Energy,[eV]'
            self.experimental_curve.label.y = 'Intensity,[a.u.]'
            # self.experimental_curve.plot_curve()
            # plt.draw()

        if experiment_name_mask in 'YbZnO_5e14-75deg':
            self.experimental_curve.src_coordinate.x = data[:, 0]
            self.experimental_curve.src_coordinate.y = data[:, 3]
            self.experimental_curve.curve_label_latex = 'YbZnO_5e14-75deg'
            self.experimental_curve.label.x = 'Energy,[eV]'
            self.experimental_curve.label.y = 'Intensity,[a.u.]'
            # self.experimental_curve.plot_curve()
            # plt.draw()

        #     -------------------- YbZnO_5e15
        if experiment_name_mask in 'YbZnO_5e15-0deg':
            self.experimental_curve.src_coordinate.x = data[:, 0]
            self.experimental_curve.src_coordinate.y = data[:, 1]
            self.experimental_curve.curve_label_latex = 'YbZnO_5e15-0deg'
            self.experimental_curve.label.x = 'Energy,[eV]'
            self.experimental_curve.label.y = 'Intensity,[a.u.]'
            # self.experimental_curve.plot_curve()
            # plt.draw()

        if experiment_name_mask in 'YbZnO_5e15-45deg':
            self.experimental_curve.src_coordinate.x = data[:, 0]
            self.experimental_curve.src_coordinate.y = data[:, 2]
            self.experimental_curve.curve_label_latex = 'YbZnO_5e15-45deg'
            self.experimental_curve.label.x = 'Energy,[eV]'
            self.experimental_curve.label.y = 'Intensity,[a.u.]'
            # self.experimental_curve.plot_curve()
            # plt.draw()

        if experiment_name_mask in 'YbZnO_5e15-75deg':
            self.experimental_curve.src_coordinate.x = data[:, 0]
            self.experimental_curve.src_coordinate.y = data[:, 3]
            self.experimental_curve.curve_label_latex = 'YbZnO_5e15-75deg'
            self.experimental_curve.label.x = 'Energy,[eV]'
            self.experimental_curve.label.y = 'Intensity,[a.u.]'
            # self.experimental_curve.plot_curve()
            # plt.draw()

    def setup_axes(self):
        plt.ion()  # Force interactive
        plt.close('all')
        plt.switch_backend('QT5Agg', )
        plt.rc('font', family='serif')
        self.figure = plt.figure()
        self.figure_manager = plt.get_current_fig_manager()
        gs = gridspec.GridSpec(1, 1)

        self.axes = self.figure.add_subplot(gs[0, 0])
        for axis in ['top', 'bottom', 'left', 'right']:
            self.axes.spines[axis].set_linewidth(2)
        # plt.subplots_adjust(top=0.85)
        # gs1.tight_layout(fig, rect=[0, 0.03, 1, 0.95])
        self.figure.tight_layout(rect=[0.03, 0.03, 1, 0.95], w_pad=1.1)

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

        self.figure.tight_layout(rect=[0.03, 0.03, 1, 0.95], w_pad=1.1)


if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')
