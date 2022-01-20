from ftplib import FTP
import os
import sys

# Directory to store the patches on switch
PATCH_DIRNAME = "skylinebotw"

def listdirs(connection,_path):
    file_list, dirs, nondirs = [], [], []
    try:
        connection.cwd(_path)
    except:
        return []

    connection.retrlines('LIST', lambda x: file_list.append(x.split()))
    for info in file_list:
        ls_type, name = info[0], info[-1]
        if ls_type.startswith('d'):
            dirs.append(name)
        else:
            nondirs.append(name)
    return dirs


def ensuredirectory(connection,root,path):
    if path not in listdirs(connection, root):
        print(f"> MKD {os.path.join(root, path)}")
        connection.mkd(f'{root}/{path}')

def sendFile(connection, localPath, sdPath):
    if not os.path.isfile(localPath):
        print("Error: ", localPath, " does not exist")
        sys.exit(-1)
    print(f"Sending {localPath}")
    print(f'> STOR {sdPath}')
    connection.storbinary(f'STOR {sdPath}', open(localPath, 'rb'))

consoleIP = sys.argv[1]
if '.' not in consoleIP:
    print(sys.argv[0], "ERROR: Please specify with `IP=[Your console's IP]`")
    sys.exit(-1)

consolePort = 5000

if len(sys.argv) < 3:
    print(sys.argv[0], "ERROR: missing version")
    sys.exit(-1)
else:
    version = sys.argv[2]

curDir = os.curdir

ftp = FTP()
print(f'Connecting to {consoleIP}:{consolePort}... ', end='')
ftp.connect(consoleIP, consolePort)
print('Connected!')

# Scan for patches
patches = []
dirContent = os.listdir(curDir)
for subPathName in dirContent:
    if os.path.isfile(os.path.join(curDir, subPathName)) and subPathName.endswith(".ips"):
        patches.append(subPathName)

if len(patches) > 0:
    ensuredirectory(ftp, '', 'atmosphere')
    ensuredirectory(ftp, '/atmosphere', 'exefs_patches')
    ensuredirectory(ftp, '/atmosphere/exefs_patches', PATCH_DIRNAME)

    for patchPath in patches:
        if os.path.exists(patchPath):
            sdPath = f'/atmosphere/exefs_patches/{PATCH_DIRNAME}/{patchPath}'
            sendFile(ftp, patchPath, sdPath)

ensuredirectory(ftp, '/atmosphere', 'contents')
ensuredirectory(ftp, '/atmosphere/contents', "01007EF00011E000")
ensuredirectory(ftp, f'/atmosphere/contents/01007EF00011E000', 'exefs')

binaryPath = f'{os.path.basename(os.getcwd())}{version}.nso'
sdPath = f'/atmosphere/contents/01007EF00011E000/exefs/subsdk9'
sendFile(ftp, binaryPath, sdPath)

metaPath = f'{os.path.basename(os.getcwd())}{version}.npdm'
sdPath = '/atmosphere/contents/01007EF00011E000/exefs/main.npdm'
sendFile(ftp, metaPath, sdPath)
