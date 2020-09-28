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