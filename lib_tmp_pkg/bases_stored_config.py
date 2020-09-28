'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 07.09.2020
'''
import logging
import pickle
import os
from typing import Optional
# from lib_pkg.dumper import dump
# from lib_pkg.bases import Variable
from lib_tmp_pkg.class_cfg import Configuration, print_object_properties_value_in_table_form, pt


class VarObject:
    def __init__(self):
        self.dict_of_stored_vars = {}

    def add_variable_to_dict(self, name: Optional[str] = None, value=None):
        if name is not None and value is not None:
            self.dict_of_stored_vars[name] = value

    def show_properties(self):
        table = pt.PrettyTable([
            'Name',
            'Value',
        ])
        for key, value in self.dict_of_stored_vars.items():
            if (not key.startswith('__')) and ('classmethod' not in str(value)):
                table.add_row(
                    [
                        str(key),
                        str(value),
                    ]
                )
        print('dict_of_stored_vars:')
        print(table)


class StoredConfigVariable:
    def __init__(self):
        self.description_line = None
        self.delimiter = None
        self.file_name_of_stored_vars = 'vars_configuration.pckl'
        self.dir_path = Configuration.PROJECT_CURRENT_OUT_DIRECTORY_PATH
        self.config = Configuration
        self.list_of_variable_dicts = {}
        self.loaded_vars = None

    def add_object_to_list_of_dicts(self, input_obj: Optional[VarObject] = None):
        if input_obj is not None:
            n = 1
            if self.list_of_variable_dicts is not None:
                n = len(self.list_of_variable_dicts) + 1
            self.list_of_variable_dicts[n] = input_obj

    def flush(self):
        self.description_line = None
        self.delimiter = None
        self.file_name_of_stored_vars = 'vars_configuration.pckl'
        self.dir_path = Configuration.PROJECT_CURRENT_OUT_DIRECTORY_PATH
        self.list_of_variable_dicts = {}
        self.loaded_vars = None

    def show(self):
        # print(dump(self))
        print_object_properties_value_in_table_form(self)
        table = pt.PrettyTable([
            'Name',
            'Value',
        ])
        for key, value in self.list_of_variable_dicts.items():
            table.add_row(
                [
                    str(key),
                    str(value.dict_of_stored_vars),
                ]
            )
        print('list_of_variable_dicts:')
        print(table)

    def store_data_to_pickle_file(self):
        if self.dir_path is None:
            self.dir_path = Configuration.PROJECT_OUT_DIRECTORY_PATH
            print('dir_path:', self.dir_path)
        pckl_file = os.path.join(self.dir_path, self.file_name_of_stored_vars)
        with open(pckl_file, 'wb') as f:
            pickle.dump([self], f)
            f.close()

    def load_data_from_pickle_file(self):
        # Getting back the objects:
        if os.path.isfile(os.path.join(self.dir_path, self.file_name_of_stored_vars)):
            pckl_file = os.path.join(self.dir_path, self.file_name_of_stored_vars)
            with open(pckl_file, 'rb') as f:
                obj = pickle.load(f)
            # print('')
            try:
                self.loaded_vars = obj[0]
                # self.last_used_file_path = obj[0].last_used_file_path
            except Exception as err:
                error_txt = 'TextConfigVariable: load_data_from_pickle_file: \n'
                error_txt = error_txt + '{} does not have needed attributes\n'.format(self.file_name_of_stored_vars)
                logging.getLogger("error_logger").error(error_txt + repr(err))
                if Configuration.DEBUG:
                    print(error_txt, repr(err))



if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')
    obj_tmp = VarObject()
    obj_tmp.add_variable_to_dict(name='v', value=10)
    obj_tmp.add_variable_to_dict(name='vv', value=100)
    obj_tmp.show_properties()
    obj = StoredConfigVariable()
    obj.description_line = 'Test description'
    obj.delimiter = '/t'
    obj.add_object_to_list_of_dicts(obj_tmp)
    obj.show()
    obj.store_data_to_pickle_file()
    obj.load_data_from_pickle_file()
    obj.show()
