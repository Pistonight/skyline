# This script compares 1.5.0 romfs and 1.6.0 romfs and generates necessary files for LayeredFS
# Usage: diffRomFs.py romfs_150 romfs_160 output
import sys, os, filecmp

if len(sys.argv) < 4:
    print("Usage: diffRomFs.py romfs_150 romfs_160 output")
    sys.exit(-1)

romfs150Dir = sys.argv[1]
romfs160Dir = sys.argv[2]
output = sys.argv[3]

diffList = []

def addToDiffList(diffList, path150):
    relPath = path150[len(romfs150Dir)+1:]
    diffList.append(relPath)

def scanPath(diffList, path150Str, path160Str):
    if not os.path.exists(path160Str):
            addToDiffList(diffList, path150Str)
            return

    if os.path.isfile(path150Str):
        same = filecmp.cmp(path150Str, path160Str)
        if not same:
            addToDiffList(diffList, path150Str)
    elif os.path.isdir(path150Str):
        dirContent = os.listdir(path150Str)
        print("Scanning", path150Str)
        for subPathName in dirContent:
            scanPath(diffList, os.path.join(path150Str, subPathName), os.path.join(path160Str, subPathName))

scanPath(diffList, romfs150Dir, romfs160Dir)

with open(output, "w+") as changeFile:
    for diff in diffList:
        print(diff)
        changeFile.write(diff+"\n")

print("Found", len(diffList), "Diffs")