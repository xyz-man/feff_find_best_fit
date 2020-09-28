# '''
# * Created by Zhenia Syryanyy (Yevgen Syryanyy)
# * e-mail: yuginboy@gmail.com
# * Last modified: 31.08.2020
# '''
import logging
from pkg_lib.pkg_files.dir_and_file_operations import PROJECT_ROOT_DIRECTORY_PATH, get_upper_folder_name
import os


DEBUG = False
ROOT_PROJECT_DIRECTORY_NAME = 'feff_generate_input_files'


# move_target_atom
# target_atom_is_stable_and_move_zero_ipot_atom
TYPE_OF_PROCEDURE_CHANGING_INPUT_STRUCTURE = 'move_target_atom'
TYPE_OF_PROCEDURE_CHANGING_INPUT_STRUCTURE = 'move_zero_ipot_atom'

print('PROJECT_FOLDER_PATH:', PROJECT_ROOT_DIRECTORY_PATH)
SRC_SLURM_RUN_FILE_NAME = 'run_initial.sl'

if 'move_target_atom' == TYPE_OF_PROCEDURE_CHANGING_INPUT_STRUCTURE:
    POLARIZATION = 103

    SRC_FEFF_INPUT_FILE_NAME = 'feff_ZnO-s-Yb-subO_{pol}.inp'.format(pol=POLARIZATION)
    # the atom whose position we want to change:
    TARGET_ATOM_TAG = 'Yb-subO'
    TARGET_ATOM_IPOT = 3

    CENTRAL_ATOM_TAG = 'O'
    CENTRAL_ATOM_IPOT = 2

    PROJECT_NAME = 'ZnO_s=[{ttag}]_p=[{pol}]'.format(ttag=TARGET_ATOM_TAG, pol=POLARIZATION)
# ------------------ End "move_target_atom" ---------------


if 'move_zero_ipot_atom' == TYPE_OF_PROCEDURE_CHANGING_INPUT_STRUCTURE:
    POLARIZATION = 103
    # CENTRAL_ATOM_TAG = 'Yb-octa'
    # CENTRAL_ATOM_TAG = 'Yb-tetra'
    # CENTRAL_ATOM_TAG = 'Yb-subZn'
    CENTRAL_ATOM_TAG = 'Yb-subO'

    CENTRAL_ATOM_IPOT = 3
    if 'sub' not in CENTRAL_ATOM_TAG:
        SRC_FEFF_INPUT_FILE_NAME = 'feff_ZnO-i-{ctag}_c=Yb_m=O_{pol}.inp'.format(ctag=CENTRAL_ATOM_TAG,
                                                                                 pol=POLARIZATION)
    if 'sub' in CENTRAL_ATOM_TAG:
        SRC_FEFF_INPUT_FILE_NAME = 'feff_ZnO-s-{ctag}_c=Yb_m=O_{pol}.inp'.format(ctag=CENTRAL_ATOM_TAG,
                                                                                 pol=POLARIZATION)

    ZERO_IPOT_ATOM_TAG = 'O'
    ZERO_IPOT_ATOM_IPOT = 2

    if 'sub' not in CENTRAL_ATOM_TAG:
        PROJECT_NAME = 'ZnO_ist=[{ctag}]_m={ttag}_c={ctag}_p=[{pol}]'.format(
            ctag=CENTRAL_ATOM_TAG,
            ttag=ZERO_IPOT_ATOM_TAG,
            pol=POLARIZATION)
    if 'sub' in CENTRAL_ATOM_TAG:
        PROJECT_NAME = 'ZnO_sub=[{ctag}]_m={ttag}_c={ctag}_p=[{pol}]'.format(
            ctag=CENTRAL_ATOM_TAG,
            ttag=ZERO_IPOT_ATOM_TAG,
            pol=POLARIZATION)

# ------------------ End "move_zero_ipot_atom" ---------------

PROJECT_OUT_DIRECTORY_PATH = '/mnt/nfsv4/abel_share/free_share/ZnO/'

# start feff calculations by using SLURM sbatch command:
START_CALCULATION = True

# local/remote:
# TYPE_OF_CALCULATION = 'local'
TYPE_OF_CALCULATION = 'remote'

# if TYPE_OF_CALCULATION='remote':
# if TYPE_OF_CALCULATION='remote' make sure PROJECT_DIR_PATH is located in the shared folder with the remote host
PATH_TO_SHARE_PROJECT_FOLDER_ON_REMOTE_HOST = '/mnt/nfsv4/abel_share/free_share/ZnO/'
SSH_COMMAND_CONNECT_TO_REMOTE_HOST = 'ssh wien2k@10.88.0.245'  # wien2k_abel
# SSH_COMMAND_CONNECT_TO_REMOTE_HOST = 'ssh wien2k@10.88.0.244'  # wien2k_paradox

# --- START Block: Computation Limit -----
# max distance for structure rebuild procedure:
TARGET_ATOM_MAX_DISTANCE = 6
MAXIMUM_LINE_NUMBER_OF_INPUT_FEFF_FILE = None
# --- END Block: Computation Limit -----

# number of FEFF calculation processes (SLURM: #SBATCH -n 4):
NUMBER_OF_TASKS = 4

if DEBUG:
    # SRC_FEFF_INPUT_FILE_NAME = 'feff_ZnO-s-Yb-subO_101.inp'
    # TARGET_ATOM_TAG = 'Yb-subO'
    # TARGET_ATOM_IPOT = 3
    # PROJECT_NAME = 'ZnO_s=[{}]_p=[101]'.format(TARGET_ATOM_TAG)
    # TYPE_OF_CALCULATION = 'local'
    # PROJECT_OUT_DIRECTORY_PATH = '/home/yugin/PycharmProjects/feff_generate_input_files/tmp'
    # TARGET_ATOM_MAX_DISTANCE = 3.25
    # # MAXIMUM_LINE_NUMBER_OF_INPUT_FEFF_FILE = 73
    # START_CALCULATION = False

    if 'move_zero_ipot_atom' == TYPE_OF_PROCEDURE_CHANGING_INPUT_STRUCTURE:
        POLARIZATION = 100
        # CENTRAL_ATOM_TAG = 'Yb-octa'
        # CENTRAL_ATOM_TAG = 'Yb-tetra'
        # CENTRAL_ATOM_TAG = 'Yb-subZn'
        CENTRAL_ATOM_TAG = 'Yb-subO'
        if 'sub' not in CENTRAL_ATOM_TAG:
            SRC_FEFF_INPUT_FILE_NAME = 'feff_ZnO-i-{ctag}_c=Yb_m=O_{pol}.inp'.format(ctag=CENTRAL_ATOM_TAG,
                                                                                     pol=POLARIZATION)
        if 'sub' in CENTRAL_ATOM_TAG:
            SRC_FEFF_INPUT_FILE_NAME = 'feff_ZnO-s-{ctag}_c=Yb_m=O_{pol}.inp'.format(ctag=CENTRAL_ATOM_TAG,
                                                                                     pol=POLARIZATION)
        CENTRAL_ATOM_IPOT = 3

        ZERO_IPOT_ATOM_TAG = 'O'
        ZERO_IPOT_ATOM_IPOT = 2

        if 'sub' not in CENTRAL_ATOM_TAG:
            PROJECT_NAME = 'ZnO_ist=[{ctag}]_m={ttag}_c={ctag}_p=[{pol}]'.format(
                ctag=CENTRAL_ATOM_TAG,
                ttag=ZERO_IPOT_ATOM_TAG,
                pol=POLARIZATION)
        if 'sub' in CENTRAL_ATOM_TAG:
            PROJECT_NAME = 'ZnO_sub=[{ctag}]_m={ttag}_c={ctag}_p=[{pol}]'.format(
                ctag=CENTRAL_ATOM_TAG,
                ttag=ZERO_IPOT_ATOM_TAG,
                pol=POLARIZATION)
        TYPE_OF_CALCULATION = 'local'
        PROJECT_OUT_DIRECTORY_PATH = '/home/yugin/PycharmProjects/feff_generate_input_files/tmp'
        TARGET_ATOM_MAX_DISTANCE = 3.25
        # MAXIMUM_LINE_NUMBER_OF_INPUT_FEFF_FILE = 73
        START_CALCULATION = False


if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')
    print(PROJECT_ROOT_DIRECTORY_PATH)
    print(get_upper_folder_name(PROJECT_ROOT_DIRECTORY_PATH))
    print(os.path.basename(PROJECT_ROOT_DIRECTORY_PATH))
    print(os.path.dirname(PROJECT_ROOT_DIRECTORY_PATH))
