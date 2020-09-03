'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 03.09.2020
'''
import logging
import pickle
import os
from pkg_lib.pkg_cfg.class_configure import Configuration
from pkg_lib.pkg_bases.class_base import BaseClass


class StoreAndLoadVars(BaseClass):
    def __init__(self):
        self.file_name_of_stored_vars = 'vars.pckl'
        self.dir_path = Configuration.PATH_TO_CONFIGURATION_DIRECTORY
        self.file_path = os.path.join(self.dir_path, 'test.txt')

        self.last_used_dir_path = Configuration.PATH_TO_ROOT_PROJECT_DIRECTORY
        self.last_used_file_path = self.file_path

    def load_data_from_pickle_file(self):
        # Getting back the objects:
        if os.path.isfile(os.path.join(self.dir_path, self.file_name_of_stored_vars)):
            pckl_file = os.path.join(self.dir_path, self.file_name_of_stored_vars)
            with open(pckl_file, 'rb') as f:
                obj = pickle.load(f)
            # print('')
            try:
                self.last_used_dir_path = obj[0].last_used_dir_path
                self.last_used_file_path = obj[0].last_used_file_path
            except Exception as err:
                error_txt = 'StoreAndLoadVars: load_data_from_pickle_file: \n'
                error_txt = error_txt + '{} does not have attribute "last_used_dir_path"\n'.format(self.file_name_of_stored_vars)
                logging.getLogger("error_logger").error(error_txt + repr(err))
                if Configuration.DEBUG:
                    print(error_txt, repr(err))

    def store_data_to_pickle_file(self):
        pckl_file = os.path.join(self.dir_path, self.file_name_of_stored_vars)
        with open(pckl_file, 'wb') as f:
            pickle.dump([self], f)
            f.close()

    def get_last_used_dir_path(self):
        self.load_data_from_pickle_file()
        return self.last_used_dir_path

    def save_last_used_dir_path(self):
        self.store_data_to_pickle_file()

    def get_last_used_file_path(self):
        self.load_data_from_pickle_file()
        return self.last_used_file_path

    def save_last_used_file_path(self):
        self.store_data_to_pickle_file()


if __name__ == '__main__':
    print('-> you run ', __file__, ' file in a main mode')
    import tkinter as tk
    from tkinter import filedialog

    a = StoreAndLoadVars()
    print('last used: {}'.format(a.get_last_used_dir_path()))
    # openfile dialoge
    root = tk.Tk()
    root.withdraw()
    dir_path = filedialog.askdirectory(initialdir=a.get_last_used_dir_path())
    if os.path.isdir(dir_path):
        a.last_used_dir_path = dir_path
        a.save_last_used_dir_path()
        print('last used: {}'.format(a.get_last_used_dir_path()))
