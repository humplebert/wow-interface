import tarfile
from datetime import datetime

global versions
versions = {
    "Retail":"retail",
    "Vanilla":"classic_era",
    "TBC":"classic"
}

# application menu
global menu_options
menu_options = {
    '1': 'WTF',
    '2': 'WTF & Interface',
    'q': 'Quit'
}

def doCompression(showHeader = False):
    if showHeader == True:
        print("World of Warcraft Interface BackUp System\n")

    buildMenu()
    action = input("Select Action: ")

    if action in menu_options.keys():
        if action == 'q':
            quit()

        directories = buildDirectoryList()
        if action != '1':
            directories_interface = buildDirectoryList('Interface')
            directories = directories + directories_interface

        doBackUp(directories)

        print("Backup complete!\n\n")
        doCompression()
    else:
        print("Invalid Selection!\n\n")
        doCompression()

def buildDirectoryList(type = 'WTF'):
    # path to WoW installation
    root  = '/mnt/c/Program Files (x86)/World of Warcraft/'
    paths = [];

    for label, version in versions.items():
        path     = root + '_' + version + '_' + '/' + type
        path_rel = version + '/' + type
        paths.append([path, path_rel])

        print("Adding " + type + " folder for " + label + " to the archive ... " + path)

    return paths

def doBackUp(directories):
    now = datetime.now()
    now = now.strftime("%Y%m%d%H%M%S")

    # path to output directory
    output   = '/mnt/c/Users/alane/OneDrive/Documents/WoW BackUps'
    filename = output + '/' + now + '.tar.gz'

    with tarfile.open(filename, 'w') as archive:
        print('Creating archive ' + filename + ' ... ')

        for directory in directories:
            archive.add(directory[0], arcname=directory[1])

    archive.close()

def buildMenu():
    menu = []

    for k,v in menu_options.items():
        menu.append('[' + k + '] ' + v)

    print("\n".join(menu))

doCompression(True)
