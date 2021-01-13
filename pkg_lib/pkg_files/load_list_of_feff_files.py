'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 11.01.2021
'''
import os
from pprint import pprint


def load_filenames_of_feff_spectra_recursively_in_dir(dir_path=None):
    out = None
    if os.path.isdir(dir_path):
        out = list()
        for root, dirs, files in os.walk(os.path.normpath(dir_path)):
            for file in files:
                if (file.endswith("xmu.dat")):
                    out.append(os.path.join(root, file))
                    # print(os.path.join(root, file))
    return out


def get_prepared_name_from_filename(filename=None, cut_dir_name=None):
    out = None
    if filename is not None and cut_dir_name is not None:
        tmp = os.path.split(filename)[0]
        tmp2 = tmp.split(cut_dir_name)[1].replace(os.path.sep, '|').replace(' ', '_')
        out = tmp2 + '|'
    return out


def get_dict_of_spectra_filenames_and_prepared_names_from_dir(dir_path=None, cut_dir_name=None):
    out = None
    if os.path.isdir(dir_path) and cut_dir_name is not None:
        out = dict()
        fn_lst = load_filenames_of_feff_spectra_recursively_in_dir(dir_path)
        i = 0
        for file in fn_lst:
            if os.path.isfile(file):
                name = get_prepared_name_from_filename(filename=file, cut_dir_name=cut_dir_name)
                out[i] = {'name': name, 'filename': file}
                i = i + 1
    return out


if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')
    out = load_filenames_of_feff_spectra_recursively_in_dir(
        '/home/yugin/PycharmProjects/feff_find_best_fit/data/tmp_theoretical/Ira/')
    get_prepared_name_from_filename(filename=out[0], cut_dir_name='Ira')
    out = get_dict_of_spectra_filenames_and_prepared_names_from_dir(
        dir_path='/home/yugin/PycharmProjects/feff_find_best_fit/data/tmp_theoretical/Ira/',
        cut_dir_name='Ira'
    )
    pprint(out)