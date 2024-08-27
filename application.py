import tarfile, os, re, shutil, json
import os, time
from datetime import datetime, timedelta
from timeit import default_timer as timer
from colorama import Fore
from colorama import Style
from rclone_python import rclone

global debug_status

path_configuration = '/home/humplebert/wowi-configuration.json'

template_configuration = {
    'path_wow_root': '',
    'path_output': '',
    'remote_upload': '',
    'debug_mode': ''
}

# game versions
versions = {
    'Retail': '_retail_',
    'Classic Era': '_classic_era_',
    'Classic': '_classic_'
}

menus = {
    'debug_mode': {
        'y': 'Yes',
        'n': 'No',
        'q': 'Quit'
    },
    'core': {
        '1': 'Archive WTF',
        '2': 'Archive WTF & Interface',
#        '3': 'Rename Interface',
#        '4': 'Restore Interface',
        'u': 'Update Configuration',
        'q': 'Quit'
    },
    'versions': {
        '1': 'Retail',
        '2': 'Classic Era',
        '3': 'Classic',
        'q': 'Quit'
    },
    'path_wow_root': {
        '1': '/mnt/c/Program Files (x86)/World of Warcraft/',
        '2': '/mnt/c/Blizzard/World of Warcraft/',
        '3': '/mnt/d/Blizzard/World of Warcraft/',
        'o': 'Other (manually define)',
        'q': 'Quit'
    },
    'path_output': {
        '1': 'onedrive:Files/Applications/WoW Backups',
        '2': 'drive:Files/Applications/WoW Backups',
        'o': 'Other (manually define)',
        'q': 'Quit'
    },
    'remote_upload': {
        'y': 'Yes',
        'n': 'No',
        'q': 'Quit'
    }
}

label_title = 'World of Warcraft Interface Management System'
prompt_path_wow_root = 'Select path to World of Warcraft root directory...'
prompt_path_output = 'Select path to rClone output directory...'
prompt_remote_upload = 'Enable remote upload using rclone?'
prompt_debug_mode = 'Enable debug mode?'

def get_menu(menu):
    return menus[menu]

def get_menu_keys(menu):
    return menus[menu].keys()

def get_debug_status():
    return 'Yes' == get_configuration('debug_mode')

def run_manager():
    print(label_title)
    print_configuration('path_wow_root','Current Root Path')
    print_configuration('path_output','Current rClone BackUp Path')
    print_configuration('remote_upload','Remote Upload Enabled')
    print_configuration('debug_mode','Debug Mode Enabled')

    if not bool(get_configuration('path_wow_root')):
        set_path('path_wow_root', prompt_path_wow_root)
        run_manager()

    if not bool(get_configuration('path_output')):
        update_configuration('path_output', prompt_path_output)
        run_manager()

    if not bool(get_configuration('remote_upload')):
        update_configuration('remote_upload', prompt_remote_upload)
        run_manager()

    if not bool(get_configuration('debug_mode')):
        update_configuration('debug_mode', prompt_debug_mode)
        run_manager()

    path_wow_root = get_configuration('path_wow_root')
    debug_status = get_debug_status()

    # build menu
    print(build_menu(get_menu('core')))
    action = input('Select Action [q]: ')
    validate_action(action, 'core')

    match action:
        case 'u':
            set_path('path_wow_root', prompt_path_wow_root)
            update_configuration('path_output', prompt_path_output)
            update_configuration('remote_upload', prompt_remote_upload)
            update_configuration('debug_mode', prompt_debug_mode)
            run_manager()

        case '3':
            print(f"\n{build_menu(get_menu('versions'))}")
            action = input('Select Rename Action: ')
            validate_action(action,'versions')

            do_interface_rename(versions[menus['versions'][action]], path_wow_root, debug_status)
            run_manager()

        case '4':
            do_interface_restore(debug_status, path_wow_root)
            run_manager()

        case _:
            folders=['WTF']
            if action != '1':
                folders.append('Interface/Addons')

            directories = {}
            directories_failed = {}

            for version in versions:
                for folder in folders:
                    paths = build_paths(versions[version], path_wow_root, folder)

                    if os.path.exists(paths['path_folder']):
                        directories[paths['path_folder']] = paths['path_rel']
                    else:
                        directories_failed.append(paths['path_folder'])

            if directories:
                print_summary("Folders added to archive", directories)

            if directories_failed:
                print_summary("Folders NOT added to archive (path is invalid)", directories_failed)

            do_interface_archive(directories, debug_status)

            print(f"{Fore.GREEN}Backup complete!{Style.RESET_ALL}\n\n")
            run_manager()

def validate_action(action, menu, default='q'):
    if 'q' == action or '' == action:
        quit()

    if '' == action and '' != default:
        return default

    if not action in get_menu_keys(menu):
        print_message_error("Invalid Selection. Zero Tolerance for Errors. Process terminated.")
        quit()

def do_interface_archive(directories, debug_status=True):
    path_output = get_configuration('path_output')
    remote_upload = get_configuration('remote_upload')
    filename = f"{get_datetime()}.tar.gz"
    print(f"Creating archive {Fore.CYAN}{filename}{Style.RESET_ALL} ...")
    time_start = timer()

    if debug_status == False:
        try:
            #todo: debug why this fails if WTF or Interface folders do not exist
            with tarfile.open(filename, 'w') as archive:
                for value in directories:
                    if os.path.exists(value):
                        archive.add(value, arcname=directories[value])

            archive.close()
        except:
            print_message_error("Failed to create archive file: {filename}")
            run_manager()

        if remote_upload == 'Yes':
            try:
                rclone.copy(filename, path_output)
            except:
                print_message_error("Failed to execute rclone upload.")
                run_manager()

            try:
                os.remove(filename)
            except:
                print_message_error("Failed to delete file: {filename}")
                run_manager()

    time_end = timer()
    print_time_execution(time_start, time_end)

def print_time_execution(time_start, time_end):
    print(f"Total Execution Time: {Fore.YELLOW}{timedelta(seconds=time_end-time_start)}{Style.RESET_ALL}")

def do_interface_rename(version, root, debug_status=True):
    folders = ['WTF','Interface']
    filename = get_datetime()
    renames = {}
    paths_new = []

    action = re.sub(r'\W+', '', input(f"Interface Name? [{filename}] "))

    if action:
        filename = action[:35]

    timer_start = timer()
    path_archives = os.path.join(root, version, 'archives')
    if os.path.exists(path_archives) == False:
        print_summary("Create /archives directory", {path_archives})

        if debug_status == False:
            os.mkdir(path_archives)

    for folder in folders:
        paths = build_paths(version, root, folder)
        path_new = os.path.join(path_archives, f"{filename}/{folder}")

        if os.path.exists(paths['path_folder']):
            if os.path.exists(path_new):
                print_message_error("Could not rename {paths['path_rel']} to {path_new} because the folder already exists.")
                print_message_abort()
                run_manager()
            else:
                renames[paths['path_folder']] = path_new
                paths_new.append(path_new)
        else:
            print_message_error("Could not rename {paths['path_rel']} because the path to the folder was invalid!")
            print_message_abort()
            run_manager()

    if renames:
        print("\nRename process initiated. This may take some time...\n")
        for k in renames:
            if debug_status == False:
                shutil.move(k, renames[k])

        print_summary("Interface folders moved to archives", paths_new)
        print(f"{Fore.GREEN}Rename process complete!{Style.RESET_ALL}")

    timer_end = timer()
    print_time_execution(timer_start, timer_end)

def do_interface_restore(version, root, debug_status=True):
    #TODO: check if /archives folder exists for the _version_
    path_archives = os.path.join(root, version, 'archives')
    if check_archive_path() == False:
        print("Archives directory not found. Process aborted.\n")
        run_manager()

    #TODO: print a list of folders in the /archives folder grouped by timestamp with timestamp converted to y-m-d h:ma format
    #TODO: run archive for current WTF/Interface in _version_
    #TODO: rename /archives folders to _version_ folders
    print('\nNYI! Goodbye!')

def build_path_archives(version, root, archives_foldername='archives'):
    return os.path.join(root, version, archives_foldername)

def check_archive_path(path_archives):
    return os.path.exists(path_archives)

def get_datetime():
    now = datetime.now()
    return now.strftime("%Y%m%d.%H%M%S")

def print_summary(header,collection):
    merged_collection = "\n    ".join(collection)
    print(f"{header}:\n    {merged_collection}")

def build_menu(options):
    menu = []

    for k, v in options.items():
        menu.append(f"({k}) {v}")

    return "\n".join(menu)

def build_paths(version, root, folder='WTF'):
    path_version = os.path.join(root,version)
    path_folder = os.path.join(path_version, folder)
    path_rel = f"{version}/{folder}"

    return {
        'path_version': path_version,
        'path_folder': path_folder,
        'path_rel': path_rel
    }

def check_path_configuration():
    if not bool(os.path.exists(path_configuration)):
        write_configuration_file(template_configuration)

def check_path_wow_root():
    if get_configuration('path_wow_root'):
        return True

    return False

def write_configuration_file(configuration_json):
    configuration_file = open(path_configuration, 'w')
    configuration_file.write(json.dumps(configuration_json))
    configuration_file.close()

def get_configuration(configuration_key='ALL'):
    check_path_configuration()

    configuration_file = open(path_configuration,)
    configuration = json.load(configuration_file)

    if configuration_key == 'ALL':
        return configuration

    if configuration_key in configuration:
        return configuration[configuration_key]

    return

def print_configuration(configuration_key, label):
    print(f"{label}: {Fore.YELLOW}{get_configuration(configuration_key)}{Style.RESET_ALL}")

def print_message_error(message):
    print(f"{Fore.RED}{message}{Style.RESET_ALL}")

def print_message_abort(message="Process aborted!"):
    print_message_error(message)

def set_path_value(action, menu):
    if 'o' == action:
        path_value = input('Enter Full Path: ')
    else:
        path_value = menu[action]

    return path_value

def set_path(configuration_key, menu_prompt, check_path=True):
    if check_path:
        check_path_configuration()

    configuration = get_configuration()

    menu = get_menu(configuration_key)

    print(f"{menu_prompt}")
    print(build_menu(menu))
    action = input('Select Option [q]: ')
    validate_action(action, configuration_key)

    path_value = set_path_value(action, menu)

    if check_path and not bool(os.path.exists(path_value)):
        print(f"{Fore.RED}Path '{path_value}' is INVALID!{Style.RESET_ALL}")
        set_path(configuration_key, menu_prompt)
    else:
        print(f"{Fore.GREEN}Path is VALID!{Style.RESET_ALL}")
        configuration[configuration_key] = path_value
        write_configuration_file(configuration)

def update_configuration(configuration_key, menu_prompt):
    configuration = get_configuration()

    menu = get_menu(configuration_key)

    print(f"{menu_prompt}")
    print(build_menu(menu))
    action = input('Select Option [q]: ')
    validate_action(action, configuration_key)

    path_value = set_path_value(action, menu)

    configuration[configuration_key] = path_value
    write_configuration_file(configuration)

run_manager()
