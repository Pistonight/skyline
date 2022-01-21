# Copies only the files that change from 1.5.0 to 1.6.0 from romfs
# Usage: minRomFs.py romfs_150 change_file out
import sys, os, shutil

if len(sys.argv) < 4:
    print("Usage: minRomFs.py romfs_150 change_file out")
    sys.exit(-1)

romfs150Dir = sys.argv[1]
change = sys.argv[2]
outputDir = sys.argv[3]

with open(change, "r") as changeFile:
    changeLines = changeFile.readlines()
    for line in changeLines:
        line = line.rstrip("\r\n")
        srcPath = os.path.join(romfs150Dir, line)
        dstPath = os.path.join(outputDir, line)
        directory = os.path.dirname(dstPath)
        os.makedirs(directory, exist_ok=True)
        shutil.copyfile(srcPath, dstPath)
        print("Copied", dstPath)
