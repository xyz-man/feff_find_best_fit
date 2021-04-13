'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 11.01.2021
'''
import os
from pprint import pprint, pformat
from loguru import logger
from copy import copy, deepcopy
from hashlib import sha256


def get_hash(val=None):
    out = None
    if val is not None:
        out = sha256(val.encode('utf-8')).hexdigest()
    return out


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
                    'model_hash': get_hash(val=mpath),
                }
        if len(out) < 1:
            logger.info(f'Can not detect any Groups for current model: {filename}.')
            logger.info('Please check the path name.')
    return out


def get_dict_of_spectra_filenames_and_prepared_names_from_dir(dir_path=None,
                                                              cut_dir_name=None,
                                                              group_name_and_mask_dict=None):
    '''

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
    return out


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
    if (list_with_filter_keys is not None) and (list_with_filter_keys is not None):
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
        cut_dir_name='Ira'
    )
    hash_list_of_constraints = [
        ['9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae'],
        ['4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d']
    ]

    hash_list_of_models_combinations = [
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('4fa178d010afc9acbab74097bd4c9920e6f2bf1da00d84f419b0bf883a3a1148',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('502a7c53c62aa02bc0191d293938acecc68ec2a5d5ed9170f0312cf2d8d1e13e',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f'),
        ('739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae'),
        ('739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5'),
        ('739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae'),
        ('739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5'),
        ('739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5'),
        ('739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('739562b9f4177d417830aeabed58e8258cb714a07bb38f093f2217ff338c5828',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae'),
        ('84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5'),
        ('84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         '9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5'),
        ('84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('84f00dbedc771113f4941701c290e92559f524b0aa4ae3b7b584c3859291221d',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5'),
        ('9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         '9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('9381d3161cd48d53f5d19aa6726388b90fd28a0d754424371037fb13772d163f',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f'),
        ('9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         '9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('9b6bee219ed2ba2ecbc3e15ae6e3a17207f9d996523e8afa27e213cac4717cae',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee'),
        ('9ec8e50d222d8b558cd8666e5876a2258b970959b2210cd9d36b186c26b6d0d5',
         'dff5c81c2bd4959087ba797b68455c6cc353b9d401bcfa0ce0912ebf1a50133f',
         'ef6aa04c20c5443ae05fb35d2b10edb4ea46ef9e61467cb67d2cb5561d75a7ee')]

    a = [
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
        (9, 4, 5),
        (1, 5, 8),
        (7, 5, 8),
    ]
    a = remove_duplicates_from_list_of_tuples(a)
    print('Input data:')
    pprint(a)

    print('keys:')
    b = [1, 7]
    pprint(b)
    print('contained keys:')
    pprint(filter_list_of_tuples_which_contained_data_from_list(input_list=a, list_with_filter_keys=b))
    print('does not contain keys:')
    b = [1, 7]
    pprint(filter_list_of_tuples_which_does_not_contain_data_from_list(input_list=a, list_with_filter_keys=b))


    bb = [
        [1, 7],
        [1, 0],
    ]
    print('keys:')
    pprint(bb)
    print('contained keys in all lists:')
    pprint(filter_list_of_tuples_which_contained_values_from_current_list_of_lists(
        input_hash_list=a,
        constraints_hash_list=bb))

    # pprint(filter_list_of_tuples_which_contained_values_from_current_list_of_lists(
    #     input_hash_list=hash_list_of_models_combinations,
    #     constraints_hash_list=hash_list_of_constraints))

    print('does not contain keys:')
    bb = [
        [1, 7],
        [1, 0],
    ]
    pprint(filter_list_of_tuples_which_does_not_contain_values_from_current_list_of_lists(
        input_hash_list=a,
        constraints_hash_list=bb))

    print('filtered by keys:')
    bb = [
        [1, 7],
        [1, 0],
    ]
    pprint(filter_list_of_tuples_by_values_from_current_list_of_lists(
        input_hash_list=a,
        constraints_hash_list=bb))

    lst = filter_list_of_tuples_by_values_from_current_list_of_lists(
        input_hash_list=hash_list_of_models_combinations,
        constraints_hash_list=hash_list_of_constraints)
    pprint(lst)
    print('')

