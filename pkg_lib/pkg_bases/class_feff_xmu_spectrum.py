'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 9/5/20
'''
class Spectrum (object):
    # base spectrum class
    def __init__(self):
        # Chi intensities vector:
        self.chi_vector = []
        # k(1/A)
        self.k_vector = []

        # user's parameters for xftf preparation ['PK'- Pavel Konstantinov, 'ID' - Iraida Demchenko]:
        self.user = 'PK'

        # R(Angstrom):
        self.r_vector = []
        # Furie transform of chi(k) intensities vector:
        self.ftr_vector = []

        self.label = 'experiment T=350 C'
        self.label_latex = 'experiment $T=350^{\circ}$ '

        self.label_latex_ideal_curve = 'ideal curve'

        # path to the stored ASCII data file:
        self.pathToLoadDataFile = os.path.join(get_folder_name(runningScriptDir), 'data', '350.chik')

        # Temp region for R-factor calculation in Angstroms:
        self.r_factor_region = np.array([0, 0])
        # region for R(FTR)-factor calculation in Angstroms:
        self.r_factor_region_ftr = np.array([1, 5])
        # region for R(chi)-factor calculation in Angstroms^-1:
        self.r_factor_region_chi_k = np.array([3.9, 12])

        # Temp array of ideal values for R-factor calculation:
        self.ideal_curve_x = []
        self.ideal_curve_y = []
        # Temp array of probing values for R-factor calculation:
        self.probe_curve_x = []
        self.probe_curve_y = []

        # array of ideal values for R(FTR)-factor calculation:
        self.ideal_curve_r = []
        self.ideal_curve_ftr = []
        # array of probing values for R(FTR)-factor calculation:
        self.probe_curve_r = []
        self.probe_curve_ftr = []

        # array of ideal values for R(chi)-factor calculation:
        self.ideal_curve_k = []
        self.ideal_curve_chi = []
        # array of probing values for R(chi)-factor calculation:
        self.probe_curve_k = []
        self.probe_curve_chi = []


        # the coefficient of intensities scaling in FTR dimention:
        self.scale_factor = 1

        # coefficient for multiplying theory spectra in FTR space
        self.scale_theory_factor_FTR = 1
        # coefficient for multiplying theory spectra in CHI space
        self.scale_theory_factor_CHI = 1


    def loadSpectrumData(self):
        # load data from ASCII file:
        data = load_chi_data(self.pathToLoadDataFile)
        self.k_vector   = data[:, 0]
        self.chi_vector = self.scale_theory_factor_CHI * data[:, 1]

        data = load_and_apply_xftf(self.pathToLoadDataFile, user=self.user)
        self.r_vector   = data[0]
        self.ftr_vector = self.scale_theory_factor_FTR * data[2] # get only the Real-part of values

        if self.user == 'PK':
            # region for R(FTR)-factor calculation in Angstroms:
            self.r_factor_region_ftr = np.array([1, 5])
            # region for R(chi)-factor calculation in Angstroms^-1:
            self.r_factor_region_chi_k = np.array([3.9, 12])
        elif self.user == 'ID':
            # region for R(FTR)-factor calculation in Angstroms:
            self.r_factor_region_ftr = np.array([1, 5])
            # region for R(chi)-factor calculation in Angstroms^-1:
            self.r_factor_region_chi_k = np.array([3.5, 11.5])

    def plotOneSpectrum_chi_k(self, line_width=2, alpha=1.0, isLabel=True):
        if isLabel:
            plt.plot(self.k_vector, self.chi_vector, lw=line_width, alpha=alpha, label=self.label_latex)
        else:
            plt.plot(self.k_vector, self.chi_vector, lw=line_width, alpha=alpha, label=None)
        plt.ylabel('$\chi(k)$', fontsize=20, fontweight='bold')
        plt.xlabel('$k$ $[\AA^{-1}]$', fontsize=20, fontweight='bold')

    def plotTwoSpectrum_chi_k(self):
        plt.plot(self.k_vector, self.chi_vector, lw=2, label=self.label_latex)
        plt.plot(self.ideal_curve_k, self.ideal_curve_chi, lw=2, label=self.label_latex_ideal_curve)
        plt.fill_between(self.probe_curve_k, self.probe_curve_k*0, self.probe_curve_chi,
        alpha=0.2, edgecolor='#1B2ACC', facecolor='#089FFF',
        linewidth=0.5, linestyle='dashdot', antialiased=True, label = '$R_{factor}$ region')
        plt.ylabel('$\chi(k)$', fontsize=20, fontweight='bold')
        plt.xlabel('$k$ $[\AA^{-1}]$', fontsize=20, fontweight='bold')

    def plotOneSpectrum_FTR_r(self, line_width=2, alpha=1.0, isLabel=True):
        if isLabel:
            plt.plot(self.r_vector, self.ftr_vector, lw=line_width, alpha=alpha, label=self.label_latex)
        else:
            plt.plot(self.r_vector, self.ftr_vector, lw=line_width, alpha=alpha, label=None)
        plt.ylabel('$FT(r)$', fontsize=20, fontweight='bold')
        plt.xlabel('$r$ $[\AA]$', fontsize=20, fontweight='bold')

    def plotTwoSpectrum_FTR_r(self):
        plt.plot(self.r_vector, self.ftr_vector, lw=2, label=self.label_latex)
        plt.plot(self.ideal_curve_r, self.ideal_curve_ftr, lw=2, label=self.label_latex_ideal_curve)
        plt.fill_between(self.probe_curve_r, self.probe_curve_r*0, self.probe_curve_ftr,
        alpha=0.2, edgecolor='#1B2ACC', facecolor='#089FFF',
        linewidth=0.5, linestyle='dashdot', antialiased=True, label = '$R_{factor}$ region')
        plt.ylabel('$FT(r)$', fontsize=20, fontweight='bold')
        plt.xlabel('$r$ $[\AA]$', fontsize=20, fontweight='bold')

    def selectPointsInRegion(self, x, y):
        # select only the points (X,Y) in the region:
        # indexMin = (np.abs(x - self.r_factor_region[0])).argmin()
        # indexMax = (np.abs(x - self.r_factor_region[1])).argmin()
        # out_x = x[indexMin:indexMax]
        # out_y = y[indexMin:indexMax]

        # replace by numba.jit
        out_x, out_y = numba_selectPointsInRegion(x, y, np.asarray(self.r_factor_region, dtype=float))

        return out_x, out_y

    def interpArraysToEqualLength(self, x1, y1, x2, y2):
        # x1,y1 - first array of x,y values
        # x2,y2 - second array of x,y values

        l1 = len(x1)
        l2 = len(x2)
        if l1>=l2:
            num = l1
            x_interp = x1
        else:
            num = l2
            x_interp = x2

        y1_out = np.interp(x_interp, x1, y1)
        y2_out = np.interp(x_interp, x2, y2)

        # return the same length 3-arrays
        return x_interp, y1_out, y2_out

    def get_R_factor(self, y_ideal=[], y_probe=[]):
        # calc R-factor
        # y_ideal - ideal curve
        # y_probe - probing curve

        # A1 = np.power(np.abs(np.subtract(y_ideal - y_probe)), 2)
        # A2 = np.power(np.abs(y_ideal), 2)
        # return (np.sum(A1) / np.sum(A2))

        # replace by numba:
        return get_R_factor_numba_v(np.asarray(y_ideal, dtype=float), np.asarray(y_probe, dtype=float))


    def get_FTR_R_factor(self):
        '''
        return R-factor of FTR [ft(r)] conversion
        note, that ideal_curve_* vectors should be prepared correctly too (it means that ideal_curve should be writes in
        ft(r)] variables)
        :return:
        '''
        self.probe_curve_x = self.r_vector
        self.probe_curve_y = self.ftr_vector * self.scale_factor
        self.ideal_curve_x, self.ideal_curve_y = self.ideal_curve_r, self.ideal_curve_ftr
        self.r_factor_region = self.r_factor_region_ftr

        x1, y1 = self.selectPointsInRegion(self.ideal_curve_x, self.ideal_curve_y)
        x2, y2 = self.selectPointsInRegion(self.probe_curve_x, self.probe_curve_y)

        x_interp, y1_out, y2_out = self.interpArraysToEqualLength(x1, y1, x2, y2)
        self.probe_curve_x = x_interp
        self.probe_curve_y = y2_out

        self.probe_curve_r = self.probe_curve_x
        self.probe_curve_ftr = self.probe_curve_y

        return self.get_R_factor(y_ideal=y1_out, y_probe=y2_out)

    def get_FTR_sigma_squared(self):
        '''
        return unbiased sample variance of FTR [ft(r)] conversion
        note, that ideal_curve_* vectors should be prepared correctly too (it means that ideal_curve should be writes in
        ft(r)] variables)
        :return:
        '''
        self.probe_curve_x = self.r_vector
        self.probe_curve_y = self.ftr_vector * self.scale_factor
        self.ideal_curve_x, self.ideal_curve_y = self.ideal_curve_r, self.ideal_curve_ftr
        self.r_factor_region = self.r_factor_region_ftr

        x1, y1 = self.selectPointsInRegion(self.ideal_curve_x, self.ideal_curve_y)
        x2, y2 = self.selectPointsInRegion(self.probe_curve_x, self.probe_curve_y)

        x_interp, y1_out, y2_out = self.interpArraysToEqualLength(x1, y1, x2, y2)
        self.probe_curve_x = x_interp
        self.probe_curve_y = y2_out

        self.probe_curve_r = self.probe_curve_x
        self.probe_curve_ftr = self.probe_curve_y

        s2 = np.sum( (y1_out - y2_out)**2 ) / (len(y1_out) - 1)
        return s2

    def get_chi_R_factor(self):
        '''
        return R-factor of chi(k) conversion
        note, that ideal_curve_* vectors should be prepared correctly too (it means that ideal_curve should be writes in
        chi(k) variables)
        :return:
        '''
        self.probe_curve_x = self.k_vector
        self.probe_curve_y = self.chi_vector
        self.ideal_curve_x, self.ideal_curve_y = self.ideal_curve_k, self.ideal_curve_chi
        self.r_factor_region = self.r_factor_region_chi_k

        x1, y1 = self.selectPointsInRegion(self.ideal_curve_x, self.ideal_curve_y)
        x2, y2 = self.selectPointsInRegion(self.probe_curve_x, self.probe_curve_y)

        x_interp, y1_out, y2_out = self.interpArraysToEqualLength(x1, y1, x2, y2)
        self.probe_curve_x = x_interp
        self.probe_curve_y = y2_out

        self.probe_curve_k = self.probe_curve_x
        self.probe_curve_chi = self.probe_curve_y
        return self.get_R_factor(y_ideal=y1_out, y_probe=y2_out)

    def get_chi_sigma_squared(self):
        '''
        return unbiased sample variance of chi(k) conversion
        note, that ideal_curve_* vectors should be prepared correctly too (it means that ideal_curve should be writes in
        chi(k) variables)
        :return:
        '''
        self.probe_curve_x = self.k_vector
        self.probe_curve_y = self.chi_vector
        self.ideal_curve_x, self.ideal_curve_y = self.ideal_curve_k, self.ideal_curve_chi
        self.r_factor_region = self.r_factor_region_chi_k

        x1, y1 = self.selectPointsInRegion(self.ideal_curve_x, self.ideal_curve_y)
        x2, y2 = self.selectPointsInRegion(self.probe_curve_x, self.probe_curve_y)

        x_interp, y1_out, y2_out = self.interpArraysToEqualLength(x1, y1, x2, y2)
        self.probe_curve_x = x_interp
        self.probe_curve_y = y2_out

        self.probe_curve_k = self.probe_curve_x
        self.probe_curve_chi = self.probe_curve_y

        s2 = np.sum((y1_out - y2_out) ** 2) / (len(y1_out) - 1)
        return s2

    def convert_ideal_curve_to_FTR(self):
        '''
        convert ideal curve variables from chi(k) to the ft(r)
        :return:
        '''
        out = xftf(self.ideal_curve_x, self.ideal_curve_y)
        self.ideal_curve_x = out[0]
        self.ideal_curve_y = out[2]
if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')
