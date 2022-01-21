import shutil, os.path
from datetime import datetime

global version, path, filename

global directory, output
directory = '/mnt/c/Program Files (x86)/World of Warcraft/'
output = '/mnt/c/Users/alane/OneDrive/Documents/WoW BackUps'

global now
now = datetime.now()
now = now.strftime("%Y%m%d%H%M%S")

def doCompression(showHeader = False):
    global options
    options = {
        '1': ("Retail","retail"),
        '2': ("Vanilla","classic_era"),
        '3': ("TBC","classic"),
        '4': "All",
        '5': "All (w/ Interface)",
        'q': "Quit"
    }

    global suboptions
    suboptions = ('1','2','3')

    if showHeader == True:
        print("World of Warcraft BackUp System\n")

    print(buildMenu())
    action = input("Select Action: ")

    if action in options.keys():
        if action == 'q':
            quit()

        if action in suboptions:
            doBackUp(action)
        else:
            doInterface = False
            if action == '5':
                doInterface = True

            for v in suboptions:
                doBackUp(v)

                if doInterface == True:
                    doBackUp(v, 'Interface')

        print("Backup complete!\n\n")
        doCompression()
    else:
        print("Invalid Selection!\n\n")
        doCompression()

def buildPaths(action, type = 'WTF'):
    global version, path, filename

    version      = options[action][1]
    version_path = '_' + version + '_'
    path         = directory + version_path + '/'
    filename     = output + '/' + type.lower() + '-' + version + '-' + now

def printBackUpNotice(action, type = 'WTF'):
    print("Backing up " + type + " folder for " + options[action][0] + " ..." + filename)

def doBackUp(action, type = 'WTF'):
    buildPaths(action, type)
    printBackUpNotice(action, type)

    if os.path.isdir(path):
        shutil.make_archive(filename, 'zip', path, type)
    else:
        print('Skipping archive because path does not exist! ' + path)

def buildMenu():
    menu = []

    for k,v in options.items():
        if k in suboptions:
            menu.append('[' + k + '] ' + v[0])
        else:
            menu.append('[' + k + '] ' + v)

    return "\n".join(menu)

doCompression(True)
