'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 03.09.2020
'''
import datetime
from settings import *
from pkg_lib.pkg_files.dir_and_file_operations import PROJECT_ROOT_DIRECTORY_PATH
import os
from pathlib import Path
from pkg_lib.pkg_bases.class_base import print_object_properties_value_in_table_form
import numpy as np
import matplotlib.pyplot as plt


class Configuration:
    DEBUG = DEBUG
    ROOT_PROJECT_DIRECTORY_NAME = ROOT_PROJECT_DIRECTORY_NAME
    PATH_TO_ROOT_PROJECT_DIRECTORY = None
    PATH_TO_CONFIGURATION_DIRECTORY = None
    PATH_TO_LOCAL_DATA_DIRECTORY = None
    PATH_TO_LOCAL_TMP_DIRECTORY = None

    EXPERIMENTAL_SPECTRA_FILE_NAME = EXPERIMENTAL_SPECTRA_FILE_NAME
    PATH_TO_EXPERIMENT_SPECTRA_FILE = None
    PATH_TO_THEORY_SPECTRA_DIRECTORY = PATH_TO_THEORY_SPECTRA_DIRECTORY

    THEORETICAL_SPECTRUM_COLUMN_NUMBER_X = 1
    THEORETICAL_SPECTRUM_COLUMN_NUMBER_Y = 3

    EXPERIMENTAL_SPECTRUM_X_SHIFT = -541.99
    EXPERIMENTAL_SPECTRUM_Y_SHIFT = -1.865
    EXPERIMENTAL_SPECTRUM_Y_SCALE = 0.853

    SPECTRUM_CALCULATION_X_MIN = -12.5
    SPECTRUM_CALCULATION_X_MAX = 40
    SPECTRUM_CALCULATION_X_STEP_SIZE = 0.05
    SPECTRUM_CALCULATION_X_STEP_SIZE = 0.5
    # region for data operation:
    SPECTRUM_CALCULATION_X_REGION = None
    # region for calculating R-factor:
    SPECTRUM_CALCULATION_R_FACTOR_REGION = np.array([-11, 25])

    STORED_VARIABLES_OF_THEORETICAL_CALCULATED_SPECTRA_FILE_NAME = 'vars_configuration.pckl'

    DPI = plt.rcParams['figure.dpi'] #get the default dpi value
    FIGURE_GEOMETRY = (1920, 20, 1920, 1180)

    @classmethod
    def validate_input_data(cls):
        try:
            pass
        except ValueError:
            print("Incorrect")

    @classmethod
    def init_cfg_folder(cls):
        dir_path = PROJECT_ROOT_DIRECTORY_PATH
        root_project_folder_name = cls.ROOT_PROJECT_DIRECTORY_NAME
        status = True
        cfg_path = PROJECT_ROOT_DIRECTORY_PATH
        data_path = PROJECT_ROOT_DIRECTORY_PATH
        tmp_path = PROJECT_ROOT_DIRECTORY_PATH
        while status:
            if root_project_folder_name == os.path.basename(dir_path):
                status = False
                cfg_path = os.path.join(dir_path, 'cfg')
                data_path = os.path.join(dir_path, 'data')
                tmp_path = os.path.join(dir_path, 'tmp')
                break
            dir_path = Path(dir_path).parent

        cls.PATH_TO_ROOT_PROJECT_DIRECTORY = dir_path
        cls.PATH_TO_CONFIGURATION_DIRECTORY = cfg_path
        cls.PATH_TO_LOCAL_DATA_DIRECTORY = data_path
        cls.PATH_TO_LOCAL_TMP_DIRECTORY = tmp_path

    # @classmethod
    # def init_feff_input_file(cls):
    #     cls.PATH_TO_SRC_FEFF_INPUT_FILE = \
    #         os.path.join(
    #             cls.PATH_TO_CONFIGURATION_DIRECTORY,
    #             'feff_inp',
    #             cls.SRC_FEFF_INPUT_FILE_NAME)
    #
    # @classmethod
    # def init_slurm_run_file(cls):
    #     cls.PATH_TO_SRC_SLURM_RUN_FILE = \
    #         os.path.join(
    #             cls.PATH_TO_CONFIGURATION_DIRECTORY,
    #             'batch_inp',
    #             cls.SRC_SLURM_RUN_FILE_NAME)
    @classmethod
    def create_calculation_region(cls):
        x_min = cls.SPECTRUM_CALCULATION_X_MIN
        x_max = cls.SPECTRUM_CALCULATION_X_MAX
        step = cls.SPECTRUM_CALCULATION_X_STEP_SIZE
        cls.SPECTRUM_CALCULATION_X_REGION = np.r_[x_min: x_max + step: step]

    @classmethod
    def init(cls):
        cls.init_cfg_folder()
        cls.PATH_TO_EXPERIMENT_SPECTRA_FILE = os.path.join(
            cls.PATH_TO_LOCAL_DATA_DIRECTORY,
            'experiment',
            cls.EXPERIMENTAL_SPECTRA_FILE_NAME
        )
        cls.create_calculation_region()
        # cls.init_feff_input_file()
        # cls.init_slurm_run_file()

    @classmethod
    def show_properties(cls):
        print_object_properties_value_in_table_form(cls)


Configuration.init()

# importing logger settings
try:
    from cfg.logger_settings import *
except Exception as e:
    # in case of any error, pass silently.
    print('===='*10)
    print('logger settings not loaded')
    print('===='*10)


if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')
    Configuration.show_properties()
