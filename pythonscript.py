import enum
import getopt
import glob
import logging
import os
import sys
from os.path import dirname, basename

import xlrd


# ---------------------------------------------------------------------------------------------------
# handle for exported file
def get_relative_paths_from_excel_file(file_path):
    logging.info("Start getting relative paths recursively from file %s", file_path)
    relative_paths_from_excel_file = []

    work_book = xlrd.open_workbook(file_path)
    sheet = work_book.sheet_by_index(0)

    last_column = sheet.ncols - 1
    for row in range(sheet.nrows):
        relative_paths_from_excel_file.append(sheet.cell_value(row, last_column))
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
    logging.debug("Your list file path %s", convert_list_file_path)
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
def get_missing_relative_paths(excel_path, folder_path, list_extension=[".jsp", ".data"]):
    list_file_relative_path_from_excel = get_relative_paths_from_excel_file(excel_path)

    list_file_path_from_folder = get_list_file_paths_from_url_and_extension(folder_path, list_extension)
    key_info_dictionary, extension = get_info_from_list_file_path(list_file_path_from_folder)
    list_relative_path_from_folder = key_info_dictionary.keys()

    logging.info("Starting compare relative paths from %s with %s", excel_path, folder_path)
    missing_relative_paths = set(list_file_relative_path_from_excel).symmetric_difference(
        set(list_relative_path_from_folder))

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


# ----------------------------------------------------------------------------------------------------
# handle event/action
class EventTypes(enum.Enum):
    GetExtension = (1,
                    'get extensions from the path',
                    {'extension_path': ''},
                    'To use this event\\action [GetExtension].'
                    ' \\n You need to provide path contains all cms to scan all possible extension')
    CompareFileAndPath = (2,
                          'compare differ key between excel file with cms folder path',
                          {'provided_path': '', 'provided_file': ''},
                          'To use this event\\action [CompareFileAndPath].'
                          ' \\n You need to provide path contains all cms with -p option '
                          'for comparing with excel file with -f option')

    def __init__(self, require_arguments, event_title, event_arguments, instruction_description):
        self.require_arguments = require_arguments
        self.event_title = event_title
        self.event_arguments = event_arguments
        self.instruction_description = instruction_description


def map_arguments_to_event():
    full_cmd_arguments = sys.argv

    # Keep all but the first
    # define list arguments
    argument_list = full_cmd_arguments[1:]
    short_options = "hi:f:p:e:"
    long_options = ["help", "input=", "file=", "path=", "extension="]

    events_to_handle = set()
    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
        print(arguments)
        for current_argument, current_value in arguments:
            if current_argument in ("-p", "--path"):
                provided_path = current_value
                EventTypes.CompareFileAndPath.event_arguments['provided_path'] = provided_path
                events_to_handle.add(EventTypes.CompareFileAndPath)
                print("Enabling special path mode with value", current_value)
            elif current_argument in ("-f", "--file"):
                provided_file = current_value
                EventTypes.CompareFileAndPath.event_arguments['provided_file'] = provided_file
                events_to_handle.add(EventTypes.CompareFileAndPath)
            elif current_argument in ("-h", "--help"):
                print("Displaying help")
            elif current_argument in ("-i", "--input"):
                print("Enabling special input mode with value", current_value)
            elif current_argument in ("-e", "--extension"):
                extension_path = current_value
                EventTypes.GetExtension.event_arguments['extension_path'] = extension_path
                events_to_handle.add(EventTypes.GetExtension)
                print("Enabling special input mode with value", current_value)
        return events_to_handle
    except getopt.error as err:
        # Output error, and return with an error code
        print(str(err))
        sys.exit(2)


def execute_event(event_type):
    if '' in event_type.event_arguments.values():
        print("You did not give enough argument to take the action :", event_type.event_title)
        print("Type \"python pythonscript.py --help\" for more information")
        return

    if event_type == EventTypes.GetExtension:
        print_extensions_from_path(event_type.event_arguments['extension_path'])
    elif event_type == EventTypes.CompareFileAndPath:
        print_missing_keys_from_path(event_type.event_arguments['provided_file'],
                                     event_type.event_arguments['provided_path'])


# process arguments
def process_arguments():
    events_to_handle = map_arguments_to_event()
    for event in events_to_handle:
        execute_event(event)

from numpy import inf

graph = {'A': {'C': 5, 'D': 1, 'E': 2}, 'B': {'H': 1, 'G': 3}, 'C': {'I': 2, 'D': 3, 'A': 5},
         'D': {'C': 3, 'A': 1, 'H': 2}, 'E': {'A': 2, 'F': 3},
         'F': {'E': 3, 'G': 1}, 'G': {'F': 1, 'B': 3, 'H': 2}, 'H': {'I': 2, 'D': 2, 'B': 1, 'G': 2},
         'I': {'C': 2, 'H': 2}}

costs = {'A': 0, 'B': inf, 'C': inf, 'D': inf, 'E': inf, 'F': inf, 'G': inf, 'H': inf, 'I': inf}

parents = {}


def search(source, target, graph, costs, parents):
    nextNode = source
    while nextNode != target:
        for neighbor in graph[nextNode]:
            if graph[nextNode][neighbor] + costs[nextNode] < costs[neighbor]:
                print("belong to nextNode and neighbor", nextNode, neighbor,  graph[nextNode][neighbor], costs[nextNode], costs[neighbor])
                costs[neighbor] = graph[nextNode][neighbor] + costs[nextNode]
                parents[neighbor] = nextNode
            del graph[neighbor][nextNode]
        del costs[nextNode]
        nextNode = min(costs, key=costs.get)
    return parents

def backpedal(source, target, searchResult):
    node = target
    backpath = [target]
    path = []
    while node != source:
        backpath.append(searchResult[node])
        node = searchResult[node]
    for i in range(len(backpath)):
        path.append(backpath[-i - 1])

    return path


# ---------------------------------------------------------------------------------------------------
# main function
if __name__ == '__main__':
    # setup_logger()
    # process_arguments()
    # print_extensions_from_path("C:/WORK/workspace/desk_individual_customer1/cms")
    # print_missing_keys_from_path("desk_individual_customer1.xls", "C:/WORK/workspace/desk_individual_customer1/cms")
    # open_program_by_path("C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")
    result = search('A', 'B', graph, costs, parents)
    # print('parent dictionary={}'.format(result))
    # print('longest path={}'.format(backpedal('A', 'B', result)))

# ---------------------------------------------------------------------------------------------------
