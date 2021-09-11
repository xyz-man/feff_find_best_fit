'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 11.01.2021
'''
import os
from pprint import pprint, pformat
from loguru import logger
from pkg_lib.pkg_cfg.class_configure import Configuration
from copy import copy, deepcopy
from hashlib import sha256
import numpy as np


def is_path_in_selected_tuple(path: str = None, tuple_of_paths: tuple = None):
    '''
    check if tuple of paths consists the selected path value
    :param path:
    :param tuple_of_paths:
    :return:
    '''
    if path is not None and tuple_of_paths is not None:
        for val in tuple_of_paths:
            if val in path:
                return True
    else:
        return False
    return False


def walk_level(top_dir, level: int = 0):
    top_dir = top_dir.rstrip(os.path.sep)
    assert os.path.isdir(top_dir)
    num_sep = top_dir.count(os.path.sep)
    for root, dirs, files in os.walk(top_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]


def get_hash(val=None):
    out = None
    if val is not None:
        out = sha256(val.encode('utf-8')).hexdigest()
    return out[-Configuration.HASH_LENGTH:]


def load_filenames_of_feff_spectra_recursively_in_dir(dir_path=None, level: int = 0):
    out = None
    if os.path.isdir(dir_path):
        out = list()
        if level == 0:
            for root, dirs, files in os.walk(os.path.normpath(dir_path)):
                for file in files:
                    if (file.endswith("xmu.dat")):
                        out.append(os.path.join(root, file))
                    # print(os.path.join(root, file))
        else:
            for root, dirs, files in walk_level(os.path.normpath(dir_path), level=level):
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
                    'model_hash': get_hash(val=mpath),
                }
                print('=='*20)
                print('mpath:', mpath)
                print('hash: ', get_hash(val=mpath))
        if len(out) < 1:
            logger.info(f'Can not detect any Groups for current model: {filename}.')
            logger.info('Please check the path name.')
    return out


def get_dict_of_spectra_filenames_and_prepared_names_from_dir(dir_path=None,
                                                              cut_dir_name=None,
                                                              group_name_and_mask_dict=None,
                                                              path_level=0,
                                                              path_black_list: tuple = None,
                                                              ):
    '''

    :param path_black_list: the tuple of black list paths
    :param path_level: level to walk and looking for xmu.dat file throw directories
    :param dir_path:
    :param cut_dir_name:
    :param group_name_and_mask_dict:
    :return:
    {
        0: {'filename': '/home/yugin/PycharmProjects/feff_find_best_fit/data/tmp_theoretical/Ira/ZnO+1O_oct/dis1/Oi+V-Zn/0.2679 '
                     '0 1/xmu.dat',
         'group_id': 3,
         'group_mask': '0.2679 0 1',
         'group_name': '75 deg',
         'model_hash': '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         'model_name': '|ZnO+1O_oct|dis1|Oi+V-Zn|',
         'model_path': '/home/yugin/PycharmProjects/feff_find_best_fit/data/tmp_theoretical/Ira/ZnO+1O_oct/dis1/Oi+V-Zn/',
         'name': '|ZnO+1O_oct|dis1|Oi+V-Zn| [75 deg]'},
        1: {'filename': '/home/yugin/PycharmProjects/feff_find_best_fit/data/tmp_theoretical/Ira/ZnO+1O_oct/dis1/Oi+V-Zn/100/xmu.dat',
         'group_id': 1,
         'group_mask': '100',
         'group_name': '0 deg',
         'model_hash': '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         'model_name': '|ZnO+1O_oct|dis1|Oi+V-Zn|',
         'model_path': '/home/yugin/PycharmProjects/feff_find_best_fit/data/tmp_theoretical/Ira/ZnO+1O_oct/dis1/Oi+V-Zn/',
         'name': '|ZnO+1O_oct|dis1|Oi+V-Zn| [0 deg]'},
     }
    '''
    # cut_group_name_dict = {}
    out = None
    if os.path.isdir(dir_path) and cut_dir_name is not None:
        out = dict()
        fn_lst = load_filenames_of_feff_spectra_recursively_in_dir(dir_path, level=path_level)
        i = 0
        for file in fn_lst:
            if os.path.isfile(file):
                if not is_path_in_selected_tuple(path=file, tuple_of_paths=path_black_list):
                    name = get_prepared_name_from_filename(filename=file, cut_dir_name=cut_dir_name)
                    if group_name_and_mask_dict is None:
                        out[i] = {'name': name,
                                  'filename': file,
                                  'group_id': None,
                                  'group_name': None,
                                  'group_mask': None,
                                  'model_name': None,
                                  'model_path': None,
                                  'model_hash': get_hash(file),
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
                else:
                    logger.info('The current file path has been found in black list: {}', os.path.dirname(file))
    return out


def is_key_list_completely_contained_in_tuple(key_list=None, input_tuple=None):
    '''
    Check if all keys: [1, 2] contain in input_tuple=(1, 2, 4, 6, 8) or (0, 2, 4, 5, 9),
    :param key_list: [1, 2]
    :param input_tuple: (0, 2, 4, 5, 9)
    :return: True for (1, 2, 4, 6, 8) and False (0, 2, 4, 5, 9)
    '''
    if key_list is not None and input_tuple is not None:
        tmp = []
        for key in key_list:
            if key not in input_tuple:
                return False
        return True
    return False


def is_any_of_keys_from_list_contains_in_tuple(key_list=None, input_tuple=None):
    '''
    Check if any of keys: [1, 2] are contained in the input_tuple=(1, 2, 4, 6,
    8) or (0, 2, 4, 5, 9),
    :param key_list: [1, 2]
    :param input_tuple: (0, 2, 4, 5, 9)
    :return:  for [1, 2] return True in (0, 2, 4, 5, 9) or False in  (0, 3, 4, 5, 9)
    '''
    if key_list is not None and input_tuple is not None:
        for key in key_list:
            if key in input_tuple:
                return True
    return False


def is_keys_are_only_partially_contained_in_the_tuple(key_list=None, input_tuple=None):
    '''
    Check if any of keys: [1, 2] are only partially contained in the input_tuple=(1, 2, 4, 6,
    8) or (0, 2, 4, 5, 9),
    :param key_list: [1, 2]
    :param input_tuple: (0, 2, 4, 5, 9)
    :return: for keys: [1, 2] return True for (0, 2, 4, 5, 9) and False for (1, 2, 4, 6, 7)
    '''
    if key_list is not None and input_tuple is not None:
        if (not is_key_list_completely_contained_in_tuple(key_list=key_list, input_tuple=input_tuple)) and \
               is_any_of_keys_from_list_contains_in_tuple(key_list=key_list, input_tuple=input_tuple):
            return True
    return False


def filter_list_of_tuples_which_contained_data_from_list(input_list=None, list_with_filter_keys=None):
    '''
    Ex:
    input_hash_list = [
        (1, 2, 4),
        (1, 3, 4),
        (1, 9, 4),
        (3, 2, 5),
        (1, 7, 6),
        (7, 2, 1),
        (1, 2, 4),
        (7, 1, 2),
        (8, 7, 2),
        (0, 1, 7),
        (2, 1, 7),
    ]
    bb = [1, 7]
    return: [(1, 7, 6), (7, 2, 1), (7, 1, 2), (0, 1, 7), (2, 1, 7)]
    :param input_list:
    :param list_with_filter_keys:
    :return:
    '''
    if (list_with_filter_keys is not None) and (list_with_filter_keys is not None):
        if len(list_with_filter_keys) > 0:
            out = []
            current_key = list_with_filter_keys.pop()
            for val_tuple in input_list:
                if current_key in list(val_tuple):
                    out.append(val_tuple)
            # print(out)
            return filter_list_of_tuples_which_contained_data_from_list(
                input_list=out, list_with_filter_keys=list_with_filter_keys)
        else:
            return input_list
    else:
        return None


def filter_list_of_tuples_which_contained_values_from_current_list_of_lists(input_hash_list=None,
                                                                            constraints_hash_list=None):
    '''
    Ex:
    input_hash_list = [
        (1, 2, 4),
        (1, 3, 4),
        (1, 9, 4),
        (3, 2, 5),
        (1, 7, 6),
        (7, 2, 1),
        (1, 2, 4),
        (7, 1, 2),
        (8, 7, 2),
        (0, 1, 7),
        (2, 1, 7),
    ]
    bb = [
        [1, 7],
        [1, 0],
    ]
    pre-return: [(1, 7, 6), (7, 2, 1), (7, 1, 2), (0, 1, 7), (2, 1, 7)]
    return: [(0, 1, 7)]

    :param input_hash_list:
    :param constraints_hash_list:
    :return:
    '''
    out = input_hash_list
    for val_lst in constraints_hash_list:
        out = filter_list_of_tuples_which_contained_data_from_list(input_list=out, list_with_filter_keys=val_lst)
    return out


def is_keys_from_the_key_list_always_have_a_pair_in_the_input_tuple(input_tuple=None, key_lists=None):
    '''
    Ex:

    :param input_list_of_tuples:
    :param key_lists:
    :return:
    '''
    out = []
    if (input_tuple is not None) and (key_lists is not None):
        uniq_keys = np.unique(key_lists)
        for u_key in uniq_keys:
            for key_val in key_lists:
                if u_key in key_val:
                    if u_key in input_tuple:
                        if is_key_list_completely_contained_in_tuple(input_tuple=input_tuple, key_list=key_val):
                            break
                        if is_keys_are_only_partially_contained_in_the_tuple(input_tuple=input_tuple, key_list=key_val):
                            return False
        return True
    return False


def filter_list_of_tuples_by_list_of_key_lists(input_list_of_tuples=None, key_lists=None):
    '''
    Ex:
    input_list_of_tuples = [
        (1, 8, 6, 2, 4),
        (1, 8, 5, 2, 4),
        (0, 1, 2, 5, 7),
        (1, 1, 2, 3, 4),
        (1, 1, 2, 3, 4),
        (1, 5, 2, 3, 4),
        (4, 2, 5, 9, 0),
        (0, 6, 3, 4, 7),
        (1, 2, 9, 8, 7)
    ]
    key_lists = [
        [1, 2],
        [1, 3],
        [4, 5],
    ]
    output:
    [(1, 2, 7, 8, 9), (1, 2, 4, 5, 8), (1, 2, 3, 4, 5)]

    :param input_list_of_tuples:
    :param key_lists:
    :return:
    '''
    out = []
    if input_list_of_tuples is not None and key_lists is not None:
        uniq_keys = np.unique(key_lists)
        for tuple_val in input_list_of_tuples:
            if is_keys_from_the_key_list_always_have_a_pair_in_the_input_tuple(
                    input_tuple=tuple_val, key_lists=key_lists
            ):
                # append only when tmp_tuple_list has some value:
                out.append(tuple_val)
    return out


# ---- does not contain:
def filter_list_of_tuples_which_does_not_contain_data_from_list(input_list=None, list_with_filter_keys=None):
    '''
        Ex:
        input_hash_list = [
            (1, 2, 4),
            (1, 3, 4),
            (1, 9, 4),
            (3, 2, 5),
            (1, 7, 6),
            (7, 2, 1),
            (1, 2, 4),
            (7, 1, 2),
            (8, 7, 2),
            (0, 1, 7),
            (2, 1, 7),
        ]
        bb = [1, 7]
        does not contain:
        return: [(3, 2, 5)]
        :param input_list:
        :param list_with_filter_keys:
        :return:
        '''
    if (input_list is not None) and (list_with_filter_keys is not None):
        if len(list_with_filter_keys) > 0:
            out = []
            current_key = list_with_filter_keys.pop()
            for val_tuple in input_list:
                if current_key not in list(val_tuple):
                    out.append(val_tuple)
            # print(out)
            return filter_list_of_tuples_which_does_not_contain_data_from_list(
                input_list=out, list_with_filter_keys=list_with_filter_keys)
        else:
            return input_list
    else:
        return None


def filter_list_of_tuples_which_does_not_contain_values_from_current_list_of_lists(input_hash_list=None,
                                                                                   constraints_hash_list=None):
    '''
    Ex:
    input_hash_list = [
        (1, 2, 4),
        (1, 3, 4),
        (1, 9, 4),
        (3, 2, 5),
        (1, 7, 6),
        (7, 2, 1),
        (1, 2, 4),
        (7, 1, 2),
        (8, 7, 2),
        (0, 1, 7),
        (2, 1, 7),
        (9, 4, 5)
    ]
    bb = [
        [1, 7],
        [1, 0],
    ]
    does not contain:
    return: [(3, 2, 5), (9, 4, 5)]

    :param input_hash_list:
    :param constraints_hash_list:
    :return:
    '''
    out = input_hash_list
    for val_lst in constraints_hash_list:
        out = filter_list_of_tuples_which_does_not_contain_data_from_list(input_list=out, list_with_filter_keys=val_lst)
    return out


# ----- does not contain and contain in each key-list in constraints_hash_list:
def filter_list_of_tuples_by_values_from_current_list_of_lists(input_hash_list=None,
                                                               constraints_hash_list=None):
    '''
    include pairs and all cases without pairs.
    Collect all cases of constraints and avoid cases with keys from unpaired constraints.
    Ex:
    Input data:
    [(1, 2, 7),
     (0, 1, 7),
     (5, 7, 8),
     (1, 3, 4),
     (2, 3, 5),
     (2, 7, 8),
     (1, 4, 9),
     (4, 5, 9),
     (1, 5, 8),
     (1, 6, 7),
     (1, 2, 4)]
    keys = [
        [1, 7],
        [1, 0],
    ]
    filtered by keys:
    return:    [(1, 2, 7), (0, 1, 7), (2, 3, 5), (4, 5, 9), (1, 6, 7)]

    :param input_hash_list:
    :param constraints_hash_list:
    :return:
    '''
    keys_list = deepcopy(constraints_hash_list)
    # get data without key values:
    out = filter_list_of_tuples_which_does_not_contain_values_from_current_list_of_lists\
        (input_hash_list=input_hash_list, constraints_hash_list=keys_list)

    # append data by values which contained key-values
    keys_list = deepcopy(constraints_hash_list)
    for val_lst in keys_list:
        lst_with_data_in_key_list = filter_list_of_tuples_which_contained_data_from_list(input_list=input_hash_list,
                                                                                         list_with_filter_keys=val_lst)
        for val in lst_with_data_in_key_list:
            out.append(val)
    return remove_duplicates_from_list_of_tuples(out)


def get_list_without_duplicates(input_list=None):
    out = None
    if input_list is not None:
        out = list(set(input_list))
    return out


def remove_duplicates_from_list_of_tuples(lst):
    return [t for t in (set(tuple(sorted(i)) for i in lst))]


if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')
    out = load_filenames_of_feff_spectra_recursively_in_dir(
        '/home/yugin/PycharmProjects/feff_find_best_fit/data/tmp_theoretical/Ira/')
    for val in out:
        print('{}'.format(os.path.dirname(val)))

    pprint(get_prepared_name_from_filename(filename=out[0], cut_dir_name='Ira'))
    print('---'*10)
    out = get_dict_of_spectra_filenames_and_prepared_names_from_dir(
        dir_path='/home/yugin/PycharmProjects/feff_find_best_fit/data/tmp_theoretical/Ira/',
        cut_dir_name='Ira',
        path_black_list=(
        '/home/yugin/PycharmProjects/feff_find_best_fit/data/tmp_theoretical/Ira/ZnO+1O_oct/dis2/',
        '/home/yugin/PycharmProjects/feff_find_best_fit/data/tmp_theoretical/Ira/ZnO+1O_oct/dis2/O_i-dis2-central/',
    ),
    )

    a = [
        (1, 8, 6, 2, 4),
        (1, 8, 5, 2, 4),
        (0, 1, 2, 5, 7),
        (1, 1, 2, 3, 4),
        (1, 1, 2, 3, 4),
        (1, 5, 2, 3, 4),
        (4, 2, 5, 9, 0),
        (0, 6, 3, 4, 7),
        (1, 2, 9, 8, 7),
        (0, 6, 9, 8, 7),
    ]
    bb = [
        [1, 2],
        [1, 3],
        [4, 5],
    ]
    print(is_key_list_completely_contained_in_tuple(key_list=[1, 2], input_tuple=(0, 1, 2, 5, 7)))
    print(is_key_list_completely_contained_in_tuple(key_list=[1, 2], input_tuple=(0, 1, 9, 5, 7)))
    a = remove_duplicates_from_list_of_tuples(a)
    print('Input data:')
    pprint(a)

    print('keys:')
    b = [1, 2]
    pprint(b)
    print('contained keys:')
    pprint(filter_list_of_tuples_which_contained_data_from_list(input_list=a, list_with_filter_keys=b))
    print('does not contain keys:')
    b = [1, 2]
    pprint(filter_list_of_tuples_which_does_not_contain_data_from_list(input_list=a, list_with_filter_keys=b))

    print('keys:')
    pprint(bb)
    print('list contains keys:')
    pprint(filter_list_of_tuples_which_contained_values_from_current_list_of_lists(
        input_hash_list=a,
        constraints_hash_list=deepcopy(bb)))

    print('does not contain keys:')
    pprint(filter_list_of_tuples_which_does_not_contain_values_from_current_list_of_lists(
        input_hash_list=a,
        constraints_hash_list=deepcopy(bb)))

    print('filtered by keys:')

    pprint(filter_list_of_tuples_by_values_from_current_list_of_lists(
        input_hash_list=a,
        constraints_hash_list=deepcopy(bb)))

    lst = filter_list_of_tuples_by_values_from_current_list_of_lists(
        input_hash_list=a,
        constraints_hash_list=deepcopy(bb))
    pprint(lst)

    print('filter_list_of_tuples_by_list_of_key_lists:')
    pprint(filter_list_of_tuples_by_list_of_key_lists(input_list_of_tuples=a, key_lists=bb))

    # hash_list_of_constraints = \
    #     [['d36b186c26b6d0d5', '27e213cac4717cae'],
    #      ['e0912ebf1a50133f', 'd36b186c26b6d0d5'],
    #      ['7d2cb5561d75a7ee', '1037fb13772d163f']]
    #
    # hash_list_of_models_combinations = \
    #     [('1037fb13772d163f', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d', 'e0912ebf1a50133f'),
    #      ('27e213cac4717cae', '3f2217ff338c5828', 'b584c3859291221d', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '3f2217ff338c5828', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '7d2cb5561d75a7ee', 'b584c3859291221d', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '3f2217ff338c5828', 'b584c3859291221d', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '7d2cb5561d75a7ee', 'b584c3859291221d', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '3f2217ff338c5828', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '3f2217ff338c5828', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('27e213cac4717cae', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '7d2cb5561d75a7ee', 'b584c3859291221d', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', '7d2cb5561d75a7ee', 'e0912ebf1a50133f'),
    #      ('27e213cac4717cae', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', '7d2cb5561d75a7ee', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '3f2217ff338c5828', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', 'b584c3859291221d', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('27e213cac4717cae', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', '27e213cac4717cae', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('27e213cac4717cae', '3f2217ff338c5828', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '7d2cb5561d75a7ee', 'b584c3859291221d', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('19b0bf883a3a1148', '3f2217ff338c5828', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('19b0bf883a3a1148', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '7d2cb5561d75a7ee', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '7d2cb5561d75a7ee', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', 'b584c3859291221d', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('27e213cac4717cae', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '3f2217ff338c5828', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '7d2cb5561d75a7ee', 'b584c3859291221d', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee'),
    #      ('1037fb13772d163f', '3f2217ff338c5828', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', '7d2cb5561d75a7ee', 'b584c3859291221d'),
    #      ('19b0bf883a3a1148', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5'),
    #      ('7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', 'b584c3859291221d', 'd36b186c26b6d0d5'),
    #      ('3f2217ff338c5828', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '27e213cac4717cae', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('3f2217ff338c5828', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('27e213cac4717cae', '3f2217ff338c5828', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '27e213cac4717cae', 'b584c3859291221d', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e')]
    #
    # hhash = \
    #     [('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', 'b584c3859291221d'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', '7d2cb5561d75a7ee', 'b584c3859291221d'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', '7d2cb5561d75a7ee', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', '7d2cb5561d75a7ee', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', 'b584c3859291221d', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', 'b584c3859291221d', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', 'b584c3859291221d', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '27e213cac4717cae', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '3f2217ff338c5828', 'b584c3859291221d', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '3f2217ff338c5828', 'b584c3859291221d', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '3f2217ff338c5828', 'b584c3859291221d', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '3f2217ff338c5828', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '3f2217ff338c5828', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '3f2217ff338c5828', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '7d2cb5561d75a7ee', 'b584c3859291221d', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '7d2cb5561d75a7ee', 'b584c3859291221d', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', '7d2cb5561d75a7ee', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', 'b584c3859291221d', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', 'b584c3859291221d', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '19b0bf883a3a1148', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '3f2217ff338c5828', 'b584c3859291221d', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '3f2217ff338c5828', 'b584c3859291221d', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '3f2217ff338c5828', 'b584c3859291221d', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '3f2217ff338c5828', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '3f2217ff338c5828', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '3f2217ff338c5828', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '7d2cb5561d75a7ee', 'b584c3859291221d', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '7d2cb5561d75a7ee', 'b584c3859291221d', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '27e213cac4717cae', '7d2cb5561d75a7ee', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '27e213cac4717cae', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '27e213cac4717cae', 'b584c3859291221d', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '27e213cac4717cae', 'b584c3859291221d', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '27e213cac4717cae', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5'),
    #      ('1037fb13772d163f', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '3f2217ff338c5828', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '3f2217ff338c5828', 'b584c3859291221d', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '3f2217ff338c5828', 'b584c3859291221d', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '3f2217ff338c5828', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('1037fb13772d163f', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '7d2cb5561d75a7ee', 'b584c3859291221d', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('1037fb13772d163f', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'e0912ebf1a50133f'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', 'b584c3859291221d', 'd36b186c26b6d0d5'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', 'b584c3859291221d', 'e0912ebf1a50133f'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', 'b584c3859291221d', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '3f2217ff338c5828', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '7d2cb5561d75a7ee', 'b584c3859291221d', 'e0912ebf1a50133f'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '7d2cb5561d75a7ee', 'b584c3859291221d', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', '7d2cb5561d75a7ee', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', 'b584c3859291221d', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', 'b584c3859291221d', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '27e213cac4717cae', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5'),
    #      ('19b0bf883a3a1148', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d', 'e0912ebf1a50133f'),
    #      ('19b0bf883a3a1148', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('19b0bf883a3a1148', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '3f2217ff338c5828', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('19b0bf883a3a1148', '3f2217ff338c5828', 'b584c3859291221d', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '3f2217ff338c5828', 'b584c3859291221d', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '3f2217ff338c5828', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('19b0bf883a3a1148', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '7d2cb5561d75a7ee', 'b584c3859291221d', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('19b0bf883a3a1148', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5'),
    #      ('27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d', 'e0912ebf1a50133f'),
    #      ('27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d', 'f0312cf2d8d1e13e'),
    #      ('27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('27e213cac4717cae', '3f2217ff338c5828', '7d2cb5561d75a7ee', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('27e213cac4717cae', '3f2217ff338c5828', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('27e213cac4717cae', '3f2217ff338c5828', 'b584c3859291221d', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('27e213cac4717cae', '3f2217ff338c5828', 'b584c3859291221d', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('27e213cac4717cae', '3f2217ff338c5828', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('27e213cac4717cae', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('27e213cac4717cae', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('27e213cac4717cae', '7d2cb5561d75a7ee', 'b584c3859291221d', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('27e213cac4717cae', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('27e213cac4717cae', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f'),
    #      ('3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5', 'f0312cf2d8d1e13e'),
    #      ('3f2217ff338c5828', '7d2cb5561d75a7ee', 'b584c3859291221d', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('3f2217ff338c5828', '7d2cb5561d75a7ee', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('3f2217ff338c5828', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e'),
    #      ('7d2cb5561d75a7ee', 'b584c3859291221d', 'd36b186c26b6d0d5', 'e0912ebf1a50133f', 'f0312cf2d8d1e13e')]
    #
    # print('len of hash_list_of_models_combinations: ', len(hash_list_of_models_combinations))
    # print('len of hhash: ', len(hhash))
    # print('hhash:')
    # pprint(filter_list_of_tuples_by_values_from_current_list_of_lists(
    #     input_hash_list=hhash,
    #     constraints_hash_list=hash_list_of_constraints), width=200)
    # print('hash_list_of_constraints is: ', hash_list_of_constraints)
    # print('hash_list_of_models_combinations:')
    # pprint(filter_list_of_tuples_by_values_from_current_list_of_lists(
    #     input_hash_list=hash_list_of_models_combinations,
    #     constraints_hash_list=hash_list_of_constraints), width=200)
    #
    # out = filter_list_of_tuples_by_list_of_key_lists(input_list_of_tuples=hash_list_of_models_combinations,
    #                                                  key_lists=hash_list_of_constraints)
    # print('filter_list_of_tuples_by_list_of_key_lists: ', len(out))
    # pprint(out, width=200)

    print('')

