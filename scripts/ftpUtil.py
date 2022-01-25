# Performs file actions on console via FTP
# Usage: ftpUtil.py command version ip
from ftplib import FTP
import os
import sys

# Directory to store the patches on switch
PATCH_DIRNAME = "skylinebotw"

if len(sys.argv) != 4:
    print("Usage: ftpUtil.py <deploy|clean|report> version ip")
    sys.exit(-1)

# Ftp wrapper
class FtpWrapper:
    def __init__(self, host, port):
        self.ftp = FTP()
        self.host = host
        self.port = port

    def connect(self):
        print(f'Connecting to {self.host}:{self.port}... ', end='')
        self.ftp.connect(self.host, self.port)
        print('Connected!')
    
    def listdirs(self,_path):
        file_list, dirs, nondirs = [], [], []
        try:
            self.ftp.cwd(_path)
        except:
            return []

        self.ftp.retrlines('LIST', lambda x: file_list.append(x.split()))
        for info in file_list:
            ls_type, name = info[0], info[-1]
            if ls_type.startswith('d'):
                dirs.append(name)
            else:
                nondirs.append(name)
        return dirs

    def ensurePath(self,pathArray):
        if len(pathArray) == 0 or (len(pathArray)==1 and pathArray[0]=="/"):
            return

        curRoot = "/"
        index = 0
        if pathArray[0] == "/":
            self.ensureDirectoryFromRoot("/", pathArray[1])
            curRoot = os.path.join(curRoot, pathArray[1])
            index = 2
        else:
            self.ensureDirectoryFromRoot("/", pathArray[0])
            curRoot = os.path.join(curRoot, pathArray[0])
            index = 1

        while index < len(pathArray):
            self.ensureDirectoryFromRoot(curRoot, pathArray[index])
            curRoot = os.path.join(curRoot, pathArray[index])
            index+=1

    def ensureDirectoryFromRoot(self, root, path):
        if path not in self.listdirs(root):
            print(f"> MKD {os.path.join(root, path)}")
            self.ftp.mkd(f'{root}/{path}')

    def sendFile(self,localPath, sdPath):
        if not os.path.isfile(localPath):
            print("Error: ", localPath, " does not exist or is not a file")
            sys.exit(-1)
        print(f"Sending {localPath}")
        print(f'> STOR {sdPath}')
        self.ftp.storbinary(f'STOR {sdPath}', open(localPath, 'rb'))

    def deleteFile(self, sdPath):
        try:
            self.ftp.delete(sdPath)
            print(f'> DELE {sdPath}')
        except:
            return

    def deleteDirectory(self, sdPath):
        try:
            self.ftp.cwd(sdPath)
        except:
            return

        file_list= []

        self.ftp.retrlines('LIST', lambda x: file_list.append(x.split()))
        for info in file_list:
            ls_type, name = info[0], info[-1]
            if ls_type.startswith('d'):
                self.deleteDirectory(os.path.join(sdPath, name))
            else:
                self.deleteFile(os.path.join(sdPath, name))

        print(f'> RMD {sdPath}')
        self.ftp.rmd(sdPath)

    def retriveFile(self, localPath, sdPath):
        print(f"Receiving {localPath}")
        with open(localPath, "wb+") as file:
            self.ftp.retrbinary(f"RETR {sdPath}", file.write)
            print(f"> RETR {sdPath}")

    def retriveDirectory(self, localPath, sdPath):
        os.makedirs(localPath, exist_ok=True)

        try:
            self.ftp.cwd(sdPath)
        except:
            return

        file_list= []

        self.ftp.retrlines('LIST', lambda x: file_list.append(x.split()))
        for info in file_list:
            ls_type, name = info[0], info[-1]
            if ls_type.startswith('d'):
                self.retriveDirectory(os.path.join(localPath, name), os.path.join(sdPath, name))
            else:
                self.retriveFile(os.path.join(localPath, name), os.path.join(sdPath, name))

def scanForPatches():
    patches = []
    patchDir = f"build{version}"
    dirContent = os.listdir(patchDir)
    for subPathName in dirContent:
        patchPath = os.path.join(patchDir, subPathName)
        if os.path.isfile(patchPath) and subPathName.endswith(".ips"):
            patches.append(subPathName)
    return patches

# Deploy
def deploy(ftpw):
    # IPS Patches
    patches = scanForPatches()
    if len(patches) > 0:
        ftpw.ensurePath(["atmosphere", "exefs_patches", PATCH_DIRNAME])

    for patchName in patches:
        patchPath = os.path.join(f"build{version}", patchName)
        if os.path.exists(patchPath):
            sdPath = f'/atmosphere/exefs_patches/{PATCH_DIRNAME}/{patchName}'
            ftpw.sendFile(patchPath, sdPath)

    # exefs
    ftpw.ensurePath(["atmosphere", "contents", "01007EF00011E000", "exefs"])
    binaryPath = f'build{version}/{os.path.basename(os.getcwd())}.nso'
    sdPath = '/atmosphere/contents/01007EF00011E000/exefs/subsdk9'
    ftpw.sendFile(binaryPath, sdPath)

    npdmPath = f'build{version}/{os.path.basename(os.getcwd())}.npdm'
    sdPath = '/atmosphere/contents/01007EF00011E000/exefs/main.npdm'
    ftpw.sendFile(npdmPath, sdPath)

# Clean
def clean(ftpw):
    ftpw.deleteDirectory(f"/atmosphere/exefs_patches/{PATCH_DIRNAME}")
    ftpw.deleteFile('/atmosphere/contents/01007EF00011E000/exefs/subsdk9')

# Get crash report
def report(ftpw):
    ftpw.ensurePath(["atmosphere", "crash_reports"])
    ftpw.retriveDirectory("crash_reports", "/atmosphere/crash_reports")
    ftpw.deleteDirectory("/atmosphere/crash_reports")

command = sys.argv[1]
version = sys.argv[2]
consoleIP = sys.argv[3]

if '.' not in consoleIP:
    print("Invalid IP:", consoleIP)
    sys.exit(-1)

consolePort = 5000
curDir = os.curdir
ftpw = FtpWrapper(consoleIP, consolePort)

if command == "deploy":
    ftpw.connect()
    deploy(ftpw)
elif command == "clean":
    ftpw.connect()
    clean(ftpw)
elif command == "report":
    ftpw.connect()
    report(ftpw)
else:
    print("Unknown command:", command)
    sys.exit(-1)

