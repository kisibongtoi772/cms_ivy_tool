import glob
from os.path import dirname, abspath, basename
import os
import xlrd
import subprocess
from pynput import keyboard
import logging
import threading
import sys


# ---------------------------------------------------------------------------------------------------
# handle for exported file
def get_relative_paths_from_excel_file(file_path):
    logging.info("Start getting relative paths recursively from file %s", file_path)
    relative_paths_from_excel_file = []

    work_book = xlrd.open_workbook(file_path)
    sheet = work_book.sheet_by_index(0)

    last_column_index = sheet.ncols - 1
    for index in range(sheet.nrows):
        relative_paths_from_excel_file.append(sheet.cell_value(index, last_column_index))
    logging.info("Finished getting relative paths from file %s ", file_path)
    return relative_paths_from_excel_file


# ---------------------------------------------------------------------------------------------------
# handle for folder
def get_list_file_paths_from_url_and_extension(path, extensions):
    list_file_path = []
    convert_list_file_path = []
    recursive_expression = '/**/*'

    logging.info("Start getting paths recursively from path %s with extension %s", path, extensions)
    for extension in extensions:
        list_file_path.extend(glob.glob(path + recursive_expression + extension, recursive=True))

    for file_path_with_back_slash in list_file_path:
        convert_list_file_path.append(convert_url_to_forward_slash(file_path_with_back_slash))

    logging.info("Finished getting paths recursively from path %s with extension %s", path, extensions)
    return convert_list_file_path


def get_info_from_list_file_path(list_file_path):
    extension_set = set()
    key_info_dictionary = dict()

    for current_path in list_file_path:
        filename, file_extension = os.path.splitext(current_path)
        extension_set.add(file_extension)

        full_path = dirname(current_path)
        name_value = basename(full_path)
        relative_path_key = full_path.split("/cms")[1]
        key_info_dictionary[relative_path_key] = name_value

    logging.info("Your dictionary relative path size is %s ", len(key_info_dictionary.keys()))
    logging.info("Your dictionary key CMS size is %s", len(key_info_dictionary.values()))
    logging.info("Your extensions could search from folder is %s", list(extension_set))
    return key_info_dictionary, extension_set


def convert_url_to_forward_slash(path):
    return path.replace('\\', '/')


# ---------------------------------------------------------------------------------------------------
# utilities
def get_missing_relative_paths(excel_path, folder_path):
    list_extension = [".jsp", ".data"]
    list_file_path_from_excel = get_relative_paths_from_excel_file(excel_path)
    list_file_path_from_folder = get_list_file_paths_from_url_and_extension(folder_path, list_extension)
    key_info_dictionary, extension = get_info_from_list_file_path(list_file_path_from_folder)
    relative_paths = key_info_dictionary.keys()

    logging.info("Starting compare relative paths from %s with %s", excel_path, folder_path)
    missing_relative_paths = set(list_file_path_from_excel).symmetric_difference(
        set(relative_paths))

    logging.info("Your missing relative path size %s", len(missing_relative_paths))
    return sorted(missing_relative_paths)


def get_all_extension_from_path(path):
    extensions = set()

    logging.info("Start scan extension from %s", path)
    for root, dirs, files in os.walk(path):
        for file_full_name in files:
            filename, file_extension = os.path.splitext(file_full_name)
            extensions.add(file_extension)

    logging.info("Finished scan extension from %s. Founded: %s", path, extensions)
    return extensions


def print_extensions_from_path(path):
    extensions = get_all_extension_from_path(path)
    for extension in extensions:
        print(extension)


def print_missing_keys_from_path(excel_path, folder_path):
    for missing_relative_path in get_missing_relative_paths(excel_path, folder_path):
        logging.info(missing_relative_path)


def setup_logger():
    logging.basicConfig(filename='myapp.log', level=logging.DEBUG)
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(logging.INFO)
    log_format = logging.Formatter('[%(asctime)s] [%(levelname)s] - %(message)s')
    handler.setFormatter(log_format)
    logging.getLogger('').addHandler(handler)


# ---------------------------------------------------------------------------------------------------
# Timer utilities
def open_program_by_path(path):
    subprocess.call(path)


def on_press(key):
    if key == keyboard.Key.esc:
        print(key)
        return False  # stop listener
    try:
        print(key)
        k = key.char  # single-char keys
    except AttributeError:
        k = key.name  # other keys
    if k in ['1', '2', 'left', 'right']:  # keys of interest
        # self.keys.append(k)  # store it in global-like variable
        print('Key pressed: ' + k)
        return True  # stop listener; remove this if want more keys


def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False


def on_activate_h():
    print('<ctrl>+<alt>+h pressed')


def on_activate_i():
    print('<ctrl>+<alt>+i pressed')


def trigger_key_listener():
    listener = {
        '<ctrl>+<alt>+h': on_activate_h,
        '<ctrl>+<alt>+i': on_activate_i,
    }
    with keyboard.GlobalHotKeys(listener) as host_keys:
        host_keys.join()


# ---------------------------------------------------------------------------------------------------
# main function
if __name__ == '__main__':
    setup_logger()
    print_extensions_from_path("C:/WORK/workspace/cob_portal_style/cms")
    print_missing_keys_from_path("PortalStyle.xls", "C:/WORK/workspace/cob_portal_style/cms")
    # open_program_by_path("C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")

# ---------------------------------------------------------------------------------------------------
