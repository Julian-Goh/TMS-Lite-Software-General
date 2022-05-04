import os
from os import path
import subprocess

def create_save_folder(folder_dir = os.path.join(os.environ['USERPROFILE'],  "Temp_Folder"), duplicate = False):
    if duplicate == True:
        if path.exists(folder_dir):
            index = 0
            loop = True
            while loop == True:
                new_dir = folder_dir + '({})'.format(index)
                if path.exists(new_dir):
                    index = index + 1
                else:
                    os.mkdir(new_dir)
                    loop = False

            return new_dir

        else:
            os.mkdir(folder_dir)
            return folder_dir
    else:
        if path.exists(folder_dir):
            #print ('File already exists')
            pass
        else:
            os.mkdir(folder_dir)
            #print ('File created')
        return folder_dir


def open_save_folder(folder_path, create_bool = False):
    err_flag = False
    if path.isdir(folder_path) == True:
        err_flag = False
        
        proc_obj = subprocess.Popen(['explorer', folder_path]
            , stdout = subprocess.PIPE ## To show output values
            , stderr = subprocess.STDOUT ## To hide err values
            )

    elif path.isdir(folder_path) == False:
        err_flag = True
        if create_bool == True:

            folder_path = create_save_folder(folder_dir = folder_path)
            proc_obj = subprocess.Popen(['explorer', folder_path]
                , stdout = subprocess.PIPE ## To show output values
                , stderr = subprocess.STDOUT ## To hide err values
                )

            err_flag = False

    if err_flag == True:
        print('Corresponding File Does Not Exist')