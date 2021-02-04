'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 11.01.2021
'''
import os
from pprint import pprint
from loguru import logger
from copy import copy, deepcopy


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


def get_group_name_and_mask_for_filename(filename=None, cut_dir_name=None, group_name_and_mask_dict=None):
    '''
    For multigroup fitting.
    group - the certain angle. The grou_name - is the angle. We will compare different spectra from different
    models for each group.
    If we have 0, 45, 75 degrees, then we build 3 graphs in which we show the experimental spectrum for the selected
    group and a respective linear combination of spectra from different models, but for a specific group (angle).
    For each graph/gropup/case we calculate R-factor and then calculate average R-factor from all graphs/cases/groups
    and use it in minimization procedure.
    model - consists the theoretical spectra for each group (angle). If we have 0, 45, 75 deg then our model will
    consist 3 subfolders with theoretical spectra for each angle.
    :param filename:
    :param cut_dir_name: 'Ira'
    :param group_name_and_mask_dict: {1: {'name': '45 deg', 'mask': 'aver'},}
    :return:out = {
                    'filename': filename,
                    'name': f'[{mname}] [{gname}]',
                    'group_id': key,
                    'group_name':  gname,
                    'group_mask':  gmask,

                    'model_name': mname,
                    'model_path': mpath,
                }
    '''
    out = None
    if filename is not None and cut_dir_name is not None and group_name_and_mask_dict is not None:
        out = dict()
        tmp0 = os.path.split(filename)[0]
        cutted_filename = tmp0.split(cut_dir_name)[1]
        for key, val in group_name_and_mask_dict.items():
            # user must be careful with path name. This loop will return only the last matched case
            gname = val['name']
            gmask = val['mask']
            if gmask in cutted_filename:
                mname = cutted_filename.split(gmask)[0].replace(os.path.sep, '|').replace(' ', '_')
                mpath = tmp0.split(gmask)[0]
                out = {
                    'filename': filename,
                    'name': f'{mname} [{gname}]',
                    'group_id': key,
                    'group_name':  gname,
                    'group_mask':  gmask,

                    'model_name': mname,
                    'model_path': mpath,
                }
        if len(out) < 1:
            logger.info(f'Can not detect any Groups for current model: {filename}.')
            logger.info('Please check the path name.')
    return out


def get_dict_of_spectra_filenames_and_prepared_names_from_dir(dir_path=None,
                                                              cut_dir_name=None,
                                                              group_name_and_mask_dict=None):
    # cut_group_name_dict = {}
    out = None
    if os.path.isdir(dir_path) and cut_dir_name is not None:
        out = dict()
        fn_lst = load_filenames_of_feff_spectra_recursively_in_dir(dir_path)
        i = 0
        for file in fn_lst:
            if os.path.isfile(file):
                name = get_prepared_name_from_filename(filename=file, cut_dir_name=cut_dir_name)
                if group_name_and_mask_dict is None:
                    out[i] = {'name': name,
                              'filename': file,
                              'group_id': None,
                              'group_name': None,
                              'group_mask': None,
                              'model_name': None,
                              'model_path': None,
                              }
                    i = i + 1
                else:
                    tmp_val = get_group_name_and_mask_for_filename(filename=file,
                                                                  cut_dir_name=cut_dir_name,
                                                                  group_name_and_mask_dict=group_name_and_mask_dict)
                    if tmp_val is not None:
                        if len(tmp_val) > 1:
                            # split data for such groups/subfolders that are
                            # not mentioned in group_name_and_mask_linker_dict
                            out[i] = copy(tmp_val)
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