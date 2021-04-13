from loguru import logger
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import *
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import sys
import os
from pkg_lib.esrf_lisa.dconv_config import *
from pprint import pprint
from pkg_lib.pkg_files.dir_and_file_operations import full_path_list_of_filenames_with_selected_ext, \
    create_out_data_folder

# *****************************************
# users parameters
# xtal=111
# th0 = -252336
a0 = 5.429445
# xtal, th0, = np.loadtxt(os.path.join(sys.path[0],"dconv_config.txt"))
print("xtal is: ", xtal)
print("th0 is: ", th0)
print("a0 is: ", a0)


# *****************************************

def callback():
    myfiles = fd.askopenfilenames(title='Choose a file')
    global mypaths
    mypaths = list(myfiles)
    print(mypaths)
    #   errmsg = 'Error!'


factorArr = np.array([[311, 20560.4204], [111, 10737.3294], [333, 31122.9881]])
print(factorArr)
for i in range(len(factorArr)):
    if factorArr[i, 0] == xtal:
        factor = factorArr[i, 1]
print(factor)


def convert():
    for i in range(len(mypaths)):
        filepath = mypaths[i]
        print(filepath)
        data = pd.read_csv(filepath, delim_whitespace=True, header=None, comment='#', usecols=transmcols)[transmcols]
        data.columns = ["mono", "ebragg", "I0_EH1", "I1_EH1", "I1_EH2", "IR_EH2"]
        # data = np.loadtxt(filepath, comments='#', skiprows=18, usecols=[0,2,5,6,8])
        # titles = np.array(['Energy', 'ebragg', 'I0_EH2', 'I1_EH2', 'IR_EH2'])
        # newdata = pd.DataFrame(data, columns=titles)
        data['#eBraggEnergy'] = factor / a0 / np.sin(np.radians((data['ebragg'] + th0) / 800000.0))
        data['mu'] = np.log(data['I0_EH1'] / data['I1_EH1'])
        data['mu_ref'] = np.log(data['I1_EH2'] / data['IR_EH2'])
        data.loc[~np.isfinite(data['mu']), 'mu'] = 0
        data.loc[~np.isfinite(data['mu_ref']), 'mu_ref'] = 0
        # data['E_meas'] = data['Energy']*1000
        outdata = pd.DataFrame(data[['#eBraggEnergy', 'I0_EH1', 'I1_EH1', 'mu', 'I1_EH2', 'IR_EH2', 'mu_ref']])
        outdata = outdata[outdata.mu != 0]
        # pprint(outdata)
        outfilepath = filepath.replace('.', '_r.')
        outdata.to_csv(outfilepath, header=True, index=False, sep=' ')
        plt.plot('#eBraggEnergy', 'mu', data=outdata)
        plt.xlabel('Energy')
        plt.ylabel('mu')
    plt.show()


def convert_fluo(file_list=None):
    out_dir = create_out_data_folder(DIR_PATH, first_part_of_folder_name='')
    for filepath in file_list:
        if '_r.dat' not in filepath:
            try:
                print(filepath)
                # data = pd.read_csv(filepath, delim_whitespace=True, header=None, comment='#', usecols=fluocols)[fluocols]
                # filepath = '/home/yugin/Documents/ESRF/src/08011071/zno3sml3_01_04.dat'
                data = pd.read_csv(filepath, delim_whitespace=True, header=None, comment='#')
                data.columns = input_column_names

                # data.columns = ["Energy", "ebragg", "I0_EH2", "I1_EH2", "IR_EH2", 'fluo01', 'fluo02', 'fluo03', 'fluo04',
                #                 'fluo05', 'fluo06', 'fluo07', 'fluo08', 'fluo09', 'fluo10', 'fluo11', 'fluo12']

                # data = np.loadtxt(filepath, comments='#', skiprows=18, usecols=[0,2,5,6,8])
                # titles = np.array(['Energy', 'ebragg', 'I0_EH2', 'I1_EH2', 'IR_EH2'])
                # newdata = pd.DataFrame(data, columns=titles)
                data['#eBraggEnergy'] = factor / a0 / np.sin(np.radians((data['ebragg'] + th0) / 800000.0))
                data['mu'] = np.log(data['I0_eh2'] / data['I1_eh2'])
                data['mu_ref'] = np.log(data['I1_eh2'] / data['IR_eh2'])
                data.loc[~np.isfinite(data['mu']), 'mu'] = 0
                data.loc[~np.isfinite(data['mu_ref']), 'mu_ref'] = 0
                data['E_meas'] = data['L_energy'] * 1000
                # data['fluo_tot']=data.iloc[:,5:17].sum(axis=1)
                data['fluo_tot'] = data.loc[:, 'fluo01':'fluo12'].sum(axis=1)
                data['fluo_norm'] = data['fluo_tot'] / data['I0_eh2']
                data.loc[~np.isfinite(data['fluo_norm']), 'fluo_norm'] = 0
                # columns = data.columns
                columns = ['#eBraggEnergy']
                for val in data.columns:
                    if '#eBraggEnergy' not in val:
                        columns.append(val)
                print(columns)

                outdata = pd.DataFrame(data[output_column_names])
                outdata_for_plot = pd.DataFrame(data[columns])

                # outdata = pd.DataFrame(data[['#eBraggEnergy', 'I0_EH2', 'I1_EH2', 'mu', 'fluo01', 'fluo02', 'fluo03', 'fluo04',
                #                              'fluo05', 'fluo06', 'fluo07', 'fluo08', 'fluo09', 'fluo10', 'fluo11', 'fluo12',
                #                              'fluo_norm', 'IR_EH2', 'mu_ref', 'E_meas']])
                outdata_for_plot = outdata_for_plot[outdata_for_plot.fluo_norm != 0]
                # print(outdata)
                outfilepath = filepath.replace('.', '_r.')
                outfilepath = os.path.join(out_dir,
                                           os.path.basename(outfilepath)
                                           )
                outdata.to_csv(outfilepath, header=True, index=False, sep=' ')
                plt.plot('#eBraggEnergy', 'fluo_norm', data=outdata_for_plot)
                plt.xlabel('Energy')
                plt.ylabel('normalized fluorescence')
            except Exception as err:
                logger.info(filepath)
                logger.error(err)
    plt.show()


if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')
    # window = Tk()
    # # add widgets here
    # lbl1 = Label(window, text='Convert many spec files to normal ascii', fg='blue', font=("Helvetica", 16))
    # lbl1.place(x=30, y=10)
    # lbl2 = Label(window, text='xtal =', fg='red', font=("Helvetica", 16))
    # lbl2.place(x=220, y=50)
    # lbl3 = Label(window, text=int(xtal), bg='orange', font=("Helvetica", 16))
    # lbl3.place(x=280, y=50)
    # lbl4 = Label(window, text='th0 =', fg='red', font=("Helvetica", 16))
    # lbl4.place(x=220, y=80)
    # lbl5 = Label(window, text=th0, bg='orange', font=("Helvetica", 16))
    # lbl5.place(x=280, y=80)
    # lbl6 = Label(window, text='a0 =', fg='red', font=("Helvetica", 16))
    # lbl6.place(x=220, y=110)
    # lbl7 = Label(window, text=a0, bg='orange', font=("Helvetica", 16))
    # lbl7.place(x=280, y=110)
    # btn1 = Button(text='Click to Open File', font=("Helvetica", 12), command=callback)
    # btn1.place(x=40, y=80)
    # btn2 = Button(text='Transm', font=("Helvetica", 12), command=convert)
    # btn2.place(x=80, y=200)
    # btn3 = Button(text='Transm+fluo', font=("Helvetica", 12), command=convert_fluo)
    # btn3.place(x=230, y=200)
    # btn4 = Button(text='Quit', font=("Helvetica", 12), command=quit)
    # btn4.place(x=350, y=260)
    # window.title('Data converter')
    # window.geometry("400x300+10+20")
    # window.mainloop()
    mypaths = [
        '/home/yugin/Documents/ESRF/src/08011071/zno3sml3_01_04.dat'
    ]
    DIR_PATH = '/home/yugin/Documents/ESRF/src/08011071'
    files_lst = full_path_list_of_filenames_with_selected_ext(DIR_PATH, ext='dat')

    convert_fluo(file_list=files_lst)