import tarfile
from datetime import datetime

menu_options = {
    '1': 'WTF',
    '2': 'WTF & Interface',
    'q': 'Quit'
}


def do_compression(show_header=False):
    if show_header:
        print("World of Warcraft Interface BackUp System\n")

    build_menu()
    action = input('Select Action: ')

    if action in menu_options.keys():
        if action == 'q':
            quit()

        directories = build_directory_list()
        if action != '1':
            directories_interface = build_directory_list('Interface')
            directories = directories + directories_interface

        do_backup(directories)

        print("Backup complete!\n\n")
        do_compression()
    else:
        print("Invalid Selection!\n\n")
        do_compression()


def build_directory_list(folder='WTF'):
    # path to WoW installation
    root = '/mnt/c/Program Files (x86)/World of Warcraft/'
    paths = []

    # game versions
    versions = {
        'Retail': 'retail',
        'Vanilla': 'classic_era',
        'TBC': 'classic'
    }

    for label, version in versions.items():
        path = root + '_' + version + '_' + '/' + folder
        path_rel = version + '/' + folder
        paths.append([path, path_rel])

        print('Adding ' + folder + ' folder for ' + label + ' to the archive ... ' + path)

    return paths


def do_backup(directories):
    now = datetime.now()
    now = now.strftime("%Y%m%d%H%M%S")

    # path to output directory
    output = '/mnt/c/Users/alane/OneDrive/Documents/WoW BackUps'
    filename = output + '/' + now + '.tar.gz'

    with tarfile.open(filename, 'w') as archive:
        print('Creating archive ' + filename + ' ... ')

        for directory in directories:
            archive.add(directory[0], arcname=directory[1])

    archive.close()


def get_menu_options():
    return {
        '1': 'WTF',
        '2': 'WTF & Interface',
        'q': 'Quit'
    }


def build_menu():
    menu = []

    for k, v in menu_options.items():
        menu.append('[' + k + '] ' + v)

    print("\n".join(menu))


do_compression(True)
